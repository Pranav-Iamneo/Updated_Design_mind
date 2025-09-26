# main.py - LangGraph-powered HLD Generator
# Streamlit gateway: picks a PRD PDF, runs the LangGraph workflow, and displays results

import os
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

import streamlit as st
import pandas as pd

# LangGraph workflow
from workflow import create_hld_workflow
from state.schema import WorkflowInput, ConfigSchema

# UI components
from diagram_publisher import render_mermaid_inline

# ---------- Pretty UI helpers ----------
STYLES = """
<style>
.card{border:1px solid #eee;border-radius:12px;padding:14px;background:#fff;margin:8px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.kv{display:grid;grid-template-columns:120px 1fr;gap:8px;font-size:14px}
.kv b{color:#555}
.pills{margin:6px 0}
.pill{display:inline-block;background:#f1f3f5;border:1px solid #e6e8eb;padding:4px 10px;border-radius:999px;margin:3px;font-size:13px}
.h3{font-weight:600;margin:18px 0 8px}
.smallmuted{font-size:12px;color:#666}
.status-success{color:#28a745;font-weight:600}
.status-processing{color:#ffc107;font-weight:600}
.status-failed{color:#dc3545;font-weight:600}
.status-pending{color:#6c757d;font-weight:600}
</style>
"""
st.markdown(STYLES, unsafe_allow_html=True)

def _to_py(o):
    """Normalize LLM JSON-ish like {'0': 'A', '1': 'B'} -> ['A','B'] recursively."""
    if isinstance(o, dict):
        keys = list(o.keys())
        if keys and all(str(k).isdigit() for k in keys):
            return [_to_py(o[str(i)]) for i in sorted(map(int, keys))]
        return {k: _to_py(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_to_py(v) for v in o]
    return o

def _as_list(x):
    x = _to_py(x)
    if x is None: return []
    return x if isinstance(x, list) else [x]

def _pills(title, items):
    if not items: return
    st.markdown(f"<div class='h3'>{title}</div>", unsafe_allow_html=True)
    st.markdown("<div class='pills'>" + "".join(f"<span class='pill'>{str(i)}</span>" for i in items) + "</div>", unsafe_allow_html=True)

def render_workflow_status(state):
    """Render workflow processing status"""
    if not state.status:
        return
    
    st.subheader("🔄 Workflow Status")
    
    status_data = []
    for stage_name, status in state.status.items():
        status_class = f"status-{status.status}"
        status_data.append({
            "Stage": stage_name.replace("_", " ").title(),
            "Status": status.status.title(),
            "Message": status.message or "",
            "Timestamp": status.timestamp.strftime("%H:%M:%S") if status.timestamp else ""
        })
    
    # Create status DataFrame
    df = pd.DataFrame(status_data)
    st.dataframe(df, use_container_width=True)
    
    # Show errors and warnings
    if state.errors:
        st.error("❌ **Errors:**")
        for error in state.errors:
            st.error(f"• {error}")
    
    if state.warnings:
        st.warning("⚠️ **Warnings:**")
        for warning in state.warnings:
            st.warning(f"• {warning}")

def render_authentication_ui(auth_data):
    """Render authentication analysis results"""
    if not auth_data:
        return
    
    _pills("Actors", auth_data.actors)
    _pills("Auth Flows", auth_data.flows)
    _pills("Threats", auth_data.threats)
    if auth_data.idp_options:
        _pills("Identity Providers", auth_data.idp_options)

def render_integrations_ui(integrations_data):
    """Render integrations analysis results"""
    if not integrations_data:
        st.info("No integrations found.")
        return
    
    rows = []
    for integration in integrations_data:
        rows.append({
            "System": integration.system,
            "Purpose": integration.purpose,
            "Protocol": integration.protocol,
            "Auth": integration.auth,
            "Endpoints": ", ".join(integration.endpoints),
            "Inputs": ", ".join(integration.data_contract.get("inputs", [])),
            "Outputs": ", ".join(integration.data_contract.get("outputs", []))
        })
    
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

def render_entities_ui(entities_data):
    """Render domain entities"""
    if not entities_data:
        st.info("No entities found.")
        return
    
    rows = []
    for entity in entities_data:
        rows.append({
            "Entity": entity.name,
            "Attributes Count": len(entity.attributes),
            "Attributes": ", ".join(entity.attributes)
        })
    
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    
    # Entity details cards
    st.markdown("<div class='h3'>Entity Details</div>", unsafe_allow_html=True)
    st.markdown("<div class='grid'>", unsafe_allow_html=True)
    for entity in entities_data:
        st.markdown(
            "<div class='card'><div style='font-weight:600;margin-bottom:6px'>"
            + entity.name + "</div>"
            + "<div class='pills'>" + "".join(f"<span class='pill'>{a}</span>" for a in entity.attributes) + "</div>"
            + "</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

def render_apis_ui(apis_data):
    """Render API specifications"""
    if not apis_data:
        st.info("No APIs found.")
        return
    
    rows = []
    for api in apis_data:
        req_fields = ", ".join(api.request.keys()) if api.request else "—"
        res_fields = ", ".join(api.response.keys()) if api.response else "—"
        
        rows.append({
            "API": api.name,
            "Description": api.description or "—",
            "Request Fields": req_fields,
            "Response Fields": res_fields
        })
    
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

def render_use_cases_ui(use_cases):
    """Render use cases"""
    if not use_cases:
        return
    
    st.markdown("<div class='h3'>Use Cases</div>", unsafe_allow_html=True)
    for uc in use_cases:
        st.markdown(f"- {uc}")

def render_nfrs_ui(nfrs):
    """Render non-functional requirements"""
    if not nfrs:
        return
    
    st.markdown("<div class='h3'>Non-Functional Requirements</div>", unsafe_allow_html=True)
    for category, items in nfrs.items():
        if items:
            st.markdown(f"**{category.capitalize()}**")
            for item in items:
                st.markdown(f"- {item}")

def render_risks_ui(risks_data):
    """Render risks and assumptions"""
    if not risks_data:
        return
    
    rows = []
    for risk in risks_data:
        rows.append({
            "ID": risk.id,
            "Description": risk.desc,
            "Assumption": risk.assumption,
            "Mitigation": risk.mitigation,
            "Impact": risk.impact,
            "Likelihood": risk.likelihood
        })
    
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

def list_requirement_pdfs(folder: str = "data") -> List[str]:
    """List available PDF files with detailed information"""
    base = Path(folder)
    if not base.exists():
        base.mkdir(parents=True, exist_ok=True)
        return []
    
    pdf_files = []
    for pdf_path in base.glob("*.pdf"):
        # Only include actual PDF files (not .gitkeep or other files)
        if pdf_path.is_file() and pdf_path.suffix.lower() == '.pdf':
            pdf_files.append(str(pdf_path))
    
    return sorted(pdf_files)

def get_pdf_info(pdf_path: str) -> Dict[str, Any]:
    """Get information about a PDF file"""
    path = Path(pdf_path)
    if not path.exists():
        return {}
    
    try:
        stat = path.stat()
        size_mb = stat.st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(stat.st_mtime)
        
        return {
            "name": path.name,
            "size_mb": round(size_mb, 2),
            "modified": modified.strftime("%Y-%m-%d %H:%M"),
            "path": str(path)
        }
    except Exception:
        return {"name": path.name, "path": str(path)}

def main():
    """Main Streamlit application"""
    st.set_page_config(page_title="DesignMind GenAI - LangGraph", layout="wide")
    st.title("🧠 DesignMind – LangGraph-Powered Architecture")
    st.caption("AI-driven High-Level Design generation using LangGraph workflows. Pick a requirements PDF and generate comprehensive architectural documentation.")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Workflow type selection
        workflow_type = st.selectbox(
            "Workflow Type",
            ["sequential", "parallel", "conditional"],
            index=0,
            help="Sequential: One stage at a time. Parallel: Some stages run concurrently. Conditional: Smart routing based on state."
        )
        
        # Diagram configuration
        st.subheader("📊 Diagram Settings")
        render_images = st.checkbox("Generate diagram images", value=True)
        image_format = st.radio("Image format", ["svg", "png"], horizontal=True, index=1)
        renderer = st.radio("Renderer", ["kroki", "mmdc"], horizontal=True, index=0)
        theme = st.selectbox("Diagram theme", ["default", "neutral", "dark"], index=0)
    
    # Main content
    left, right = st.columns([2, 1])
    
    with left:
        pdf_files = list_requirement_pdfs()
        file_names = [Path(p).name for p in pdf_files]
        options = ["— Select a requirements file —"] + file_names
        selected_label = st.selectbox("Requirements document:", options, index=0)
    
    with right:
        st.info(f"🔧 **Workflow:** {workflow_type.title()}")
        if pdf_files:
            st.success(f"📁 Found {len(pdf_files)} PDF files")
            
            # Show PDF file details
            with st.expander("📋 View PDF Details", expanded=False):
                pdf_data = []
                for pdf_path in pdf_files:
                    info = get_pdf_info(pdf_path)
                    if info:
                        pdf_data.append({
                            "File": info["name"],
                            "Size (MB)": info.get("size_mb", "N/A"),
                            "Modified": info.get("modified", "N/A")
                        })
                
                if pdf_data:
                    df = pd.DataFrame(pdf_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("📁 No PDF files found in `data/` folder")
            st.info("💡 **Tip:** Upload PDF files to the `data/` folder to get started.")
    
    # Get selected PDF path and show file info
    selected_path = None
    if selected_label != "— Select a requirements file —":
        try:
            selected_index = file_names.index(selected_label)
            selected_path = pdf_files[selected_index]
            
            # Show selected file information
            if selected_path:
                info = get_pdf_info(selected_path)
                if info:
                    st.info(f"📄 **Selected:** {info['name']} ({info.get('size_mb', 'N/A')} MB)")
        except ValueError:
            selected_path = None
    
    # Generate HLD button
    if st.button("🚀 Generate HLD", type="primary", disabled=not selected_path):
        if not selected_path:
            st.warning("Please choose a requirements PDF.")
            st.stop()
        
        # Create configuration
        config = ConfigSchema(
            render_images=render_images,
            image_format=image_format,
            renderer=renderer,
            theme=theme
        )
        
        # Create workflow input
        workflow_input = WorkflowInput(
            pdf_path=selected_path,
            config=config
        )
        
        # Create and run workflow
        workflow = create_hld_workflow(workflow_type)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        with st.spinner(f"🔄 Running {workflow_type} workflow..."):
            try:
                # Run workflow
                result = workflow.run(workflow_input)
                
                progress_bar.progress(100)
                
                if result.success:
                    status_placeholder.success(f"✅ HLD generated successfully in {result.processing_time:.2f}s")
                    
                    # Display results
                    state = result.state
                    
                    # Workflow status
                    render_workflow_status(state)
                    
                    # Extracted requirements
                    if state.extracted:
                        st.header("📋 Extracted Requirements")
                        with st.expander("View extracted content", expanded=False):
                            st.code(state.extracted.markdown[:5000] + "..." if len(state.extracted.markdown) > 5000 else state.extracted.markdown)
                    
                    # Authentication
                    if state.authentication:
                        st.header("🔐 Authentication")
                        render_authentication_ui(state.authentication)
                    
                    # Integrations
                    if state.integrations:
                        st.header("🔗 Integrations")
                        render_integrations_ui(state.integrations)
                    
                    # Domain entities
                    if state.domain and state.domain.entities:
                        st.header("🏗️ Domain Entities")
                        render_entities_ui(state.domain.entities)
                    
                    # APIs
                    if state.domain and state.domain.apis:
                        st.header("🔌 APIs")
                        render_apis_ui(state.domain.apis)
                    
                    # Use cases
                    if state.behavior and state.behavior.use_cases:
                        st.header("📝 Use Cases")
                        render_use_cases_ui(state.behavior.use_cases)
                    
                    # NFRs
                    if state.behavior and state.behavior.nfrs:
                        st.header("⚡ Non-Functional Requirements")
                        render_nfrs_ui(state.behavior.nfrs)
                    
                    # Risks
                    if state.behavior and state.behavior.risks:
                        st.header("⚠️ Risks & Assumptions")
                        render_risks_ui(state.behavior.risks)
                    
                    # Risk heatmap
                    if result.output_paths.get("risk_heatmap"):
                        st.header("🎯 Risk Heatmap")
                        st.image(result.output_paths["risk_heatmap"], caption="Impact × Likelihood (1..5)")
                    
                    # Diagrams
                    if state.diagrams:
                        st.header("📊 Diagrams")
                        
                        # Class diagram
                        if state.diagrams.class_text:
                            st.subheader("🏗️ Class Diagram")
                            render_mermaid_inline(state.diagrams.class_text, key="class", height=560, theme=theme)
                        
                        # Sequence diagrams
                        if state.diagrams.sequence_texts:
                            st.subheader("🔄 Sequence Diagrams")
                            for i, seq_text in enumerate(state.diagrams.sequence_texts, 1):
                                st.markdown(f"**Sequence #{i}**")
                                render_mermaid_inline(seq_text, key=f"seq-{i}", height=460, theme=theme)
                    
                    # Download section
                    st.header("💾 Downloads")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if result.output_paths.get("hld_md"):
                            with open(result.output_paths["hld_md"], "rb") as f:
                                st.download_button(
                                    "📄 Download HLD.md",
                                    data=f,
                                    file_name="HLD.md",
                                    mime="text/markdown"
                                )
                    
                    with col2:
                        if result.output_paths.get("hld_html"):
                            with open(result.output_paths["hld_html"], "rb") as f:
                                st.download_button(
                                    "🌐 Download HLD.html",
                                    data=f,
                                    file_name="HLD.html",
                                    mime="text/html"
                                )
                    
                    with col3:
                        if result.output_paths.get("diagrams_html"):
                            with open(result.output_paths["diagrams_html"], "rb") as f:
                                st.download_button(
                                    "📊 Download Diagrams.html",
                                    data=f,
                                    file_name="Diagrams.html",
                                    mime="text/html"
                                )
                    
                    # Output info
                    if state.output:
                        st.info(f"📁 **Output directory:** `{state.output.output_dir}`")
                    
                    st.caption(f"⏱️ Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                else:
                    status_placeholder.error("❌ HLD generation failed")
                    st.error("**Errors:**")
                    for error in result.errors:
                        st.error(f"• {error}")
                    
                    if result.warnings:
                        st.warning("**Warnings:**")
                        for warning in result.warnings:
                            st.warning(f"• {warning}")
            
            except Exception as e:
                progress_bar.progress(0)
                status_placeholder.error(f"❌ Workflow execution failed: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main()