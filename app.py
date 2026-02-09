import streamlit as st
import os
import time
import json
import pandas as pd
import matplotlib
import re

# --- 1. CRITICAL STABILITY SETTINGS ---
# Prevent Matplotlib from crashing the server
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Fix 'Pillow' library compatibility for WordCloud
from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

import streamlit.components.v1 as components
from wordcloud import WordCloud
from io import BytesIO
from src.utils import save_uploaded_file, validate_pdf, setup_output_dir, create_image_zip, cleanup_temp_files
from src.extractor import process_pdf, translate_content
from src.persona_intel import run_persona_intelligence

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PDF Extractor Pro",
    #page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 3. PREMIUM UI CSS ---
st.markdown("""
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />
    </head>
    <style>
        /* BASE STYLES */
        .stApp {
            background-color: #0E1117;
            font-family: 'Inter', sans-serif;
        }
        
        /* Subtle Gradient Background */
        .stApp::before {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 600px;
            background: linear-gradient(180deg, rgba(99, 102, 241, 0.08) 0%, rgba(0,0,0,0) 100%);
            pointer-events: none;
            z-index: -1;
        }

        /* HERO TYPOGRAPHY */
        .main-header {
            text-align: center;
            padding: 40px 0;
        }
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(to right, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            letter-spacing: -1px;
        }
        .sub-title {
            font-size: 1.1rem;
            color: #94a3b8;
            font-weight: 400;
        }

        /* GLASS CARDS (Using Streamlit Containers) */
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            transition: all 0.3s ease;
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div:hover {
            border-color: rgba(99, 102, 241, 0.3) !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }

        /* UPLOAD ZONE */
        [data-testid='stFileUploader'] {
            padding: 30px;
            border-radius: 16px;
            border: 2px dashed rgba(255, 255, 255, 0.1);
            background-color: rgba(255, 255, 255, 0.01);
            transition: 0.3s;
        }
        [data-testid='stFileUploader']:hover {
            border-color: #818cf8;
            background-color: rgba(99, 102, 241, 0.05);
        }

        /* TABS (Centered & Segmented) */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(255, 255, 255, 0.03);
            padding: 6px;
            border-radius: 16px;
            gap: 8px;
            display: flex;
            justify-content: center; /* Centers the tabs */
            margin: 0 auto 30px auto; /* Centers the container */
            border: 1px solid rgba(255,255,255,0.05);
            width: fit-content;
        }
        .stTabs [data-baseweb="tab"] {
            border: none;
            background: transparent;
            color: #94a3b8;
            font-weight: 600;
            padding: 10px 24px;
            border-radius: 10px;
            font-size: 0.95rem;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #fff;
            background-color: rgba(255,255,255,0.05);
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #6366f1;
            color: white;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        /* BUTTONS */
        .stButton button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
            font-weight: 600;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 8px;
            transition: 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 15px rgba(99, 102, 241, 0.3);
        }

        /* SECTION HEADERS */
        .section-header {
            display: flex;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .header-icon-box {
            width: 36px; height: 36px;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            margin-right: 12px;
            color: #818cf8;
        }
        .header-text {
            font-size: 1.4rem;
            font-weight: 700;
            color: #fff;
        }
        
        /* TEXT AREAS */
        .stTextArea textarea {
            background-color: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            color: #e2e8f0;
        }
    </style>
""", unsafe_allow_html=True)

# --- 4. MAIN LOGIC ---

# Session State
if 'processed' not in st.session_state: st.session_state.processed = False
if 'data' not in st.session_state: st.session_state.data = {}
if 'translated_text' not in st.session_state: st.session_state.translated_text = ""

# Header
st.markdown("""
    <div class="main-header">
        <div class="main-title">PDF Extractor Pro</div>
        <div class="sub-title">Simple Extraction. Powerful Insights.</div>
    </div>
""", unsafe_allow_html=True)

# Upload
c_left, c_center, c_right = st.columns([1, 2, 1])
with c_center:
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

if not uploaded_file:
    st.markdown('<div style="text-align:center;color:#64748b;margin-top:16px;font-size:0.9rem;">Supported Format: PDF (Max 200MB)</div>', unsafe_allow_html=True)
else:
    file_path = save_uploaded_file(uploaded_file)
    is_valid, is_encrypted, doc_or_err = validate_pdf(file_path)
    password = None

    if not is_valid:
        st.error(f"⚠️ {doc_or_err}")
    else:
        # Center controls for consistent alignment with the uploader
        _, c_control_group, _ = st.columns([1, 2, 1])

        with c_control_group:
            if is_encrypted:
                password = st.text_input("Enter Password", type="password")

            st.markdown("<br>", unsafe_allow_html=True)

            if not is_encrypted or (is_encrypted and password):
                if st.button("Initialize Analysis", type="primary", use_container_width=True):
                    # Progress Animation
                    progress_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    progress_text.markdown("**Reading document structure...**")
                    progress_bar.progress(25)
                    output_dir = setup_output_dir(uploaded_file.name)
                    doc = doc_or_err
                    
                    progress_text.markdown("**Extracting text and assets...**")
                    progress_bar.progress(60)
                    
                    # Core Extraction Logic
                    text_preview, img_count, struct_data, proc_status = process_pdf(doc, output_dir, file_path, password)
                    
                    if proc_status == "SUCCESS":
                        progress_text.markdown("**Finalizing...**")
                        progress_bar.progress(90)
                        zip_path = create_image_zip(output_dir)
                        
                        progress_bar.progress(100)
                        time.sleep(0.5)
                        st.session_state.processed = True
                        st.session_state.data = {
                            "text_path": struct_data["text_path"], 
                            "structure": struct_data,
                            "img_count": img_count,
                            "output_dir": output_dir,
                            "file_path": file_path,
                            "zip_path": zip_path,
                            "filename": uploaded_file.name,
                            "filesize": f"{uploaded_file.size / 1024 / 1024:.2f} MB"
                        }
                        st.session_state.translated_text = ""
                        doc.close() 
                        cleanup_temp_files(file_path)
                        st.rerun()
                    elif proc_status == "INVALID_PASSWORD":
                        st.error("Incorrect Password")

# --- 5. DASHBOARD ---
if st.session_state.processed:
    st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
    
    data = st.session_state.data
    struct = data.get("structure", {})
    pdf_meta = struct.get("pdf_meta", {})
    tables = struct.get("tables", [])
    
    try:
        with open(data["text_path"], "r", encoding="utf-8") as f:
            full_text_content = f.read()
    except:
        full_text_content = ""

    # Navigation
    t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
        "Metadata", "Structure", "Reader", "Tables", "Visuals", "Gallery", "Export", "Persona AI"
    ])

    # 1. Metadata
    with t1:
        st.markdown("""
            <div class="section-header">
                <div class="header-icon-box"><span class="material-symbols-rounded">info</span></div>
                <div class="header-text">Document DNA</div>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.container(border=True): st.caption("FILENAME"); st.markdown(f"**{data['filename']}**")
        with c2:
            with st.container(border=True): st.caption("FILE SIZE"); st.markdown(f"**{data['filesize']}**")
        with c3:
            with st.container(border=True): st.caption("TITLE"); st.markdown(f"**{struct.get('title', 'N/A')}**")
        
        st.markdown("<br>", unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4:
            with st.container(border=True): st.caption("AUTHOR"); st.markdown(f"**{pdf_meta.get('author', 'Unknown')}**")
        with c5:
            with st.container(border=True): st.caption("PRODUCER"); st.markdown(f"**{pdf_meta.get('producer', 'Unknown')}**")
        with c6:
            with st.container(border=True): st.caption("CREATED"); st.markdown(f"**{pdf_meta.get('creationDate', 'Unknown').replace('D:', '').split('+')[0]}**")

    # 2. Structure
    with t2:
        st.markdown("""
            <div class="section-header">
                <div class="header-icon-box"><span class="material-symbols-rounded">toc</span></div>
                <div class="header-text">Semantic Outline</div>
            </div>
        """, unsafe_allow_html=True)
        
        outline = struct.get("outline", [])
        if outline:
            for item in outline:
                st.markdown(f"""
                    <div style='padding:12px; border-bottom:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;'>
                        <span style="font-weight:500;">{item['text']}</span>
                        <span style='color:#64748b; font-size:0.85rem; background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px;'>Pg {item['page']}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No bookmarks found.")

    # 3. Reader
    with t3:
        st.markdown("""
            <div class="section-header">
                <div class="header-icon-box"><span class="material-symbols-rounded">translate</span></div>
                <div class="header-text">Universal Reader</div>
            </div>
        """, unsafe_allow_html=True)
        
        langs = {"Spanish": "es", "French": "fr", "German": "de", "Hindi": "hi", "Chinese": "zh-CN"}
        col_ctrl, col_fill = st.columns([1, 3])
        with col_ctrl:
            sel_lang = st.selectbox("Translate to:", ["None"] + list(langs.keys()), label_visibility="collapsed")
        
        if sel_lang != "None" and st.button("Translate Text", use_container_width=True):
            with st.spinner("Translating..."):
                res = translate_content(full_text_content[:5000], langs.get(sel_lang))
                if len(full_text_content) > 5000: res += "\n\n[Truncated]"
                st.session_state.translated_text = res
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: 
            st.caption("ORIGINAL TEXT")
            st.text_area("Original", full_text_content, height=500, label_visibility="collapsed")
        with c2: 
            st.caption(f"TRANSLATED ({sel_lang})")
            st.text_area("Translated", st.session_state.translated_text, height=500, label_visibility="collapsed")

    # 4. Tables
    with t4:
        st.markdown("""
            <div class="section-header">
                <div class="header-icon-box"><span class="material-symbols-rounded">table_chart</span></div>
                <div class="header-text">Extracted Tables</div>
            </div>
        """, unsafe_allow_html=True)
        
        if tables:
            for i, tbl in enumerate(tables):
                with st.expander(f"Table {i+1} (Page {tbl['page']})"): st.dataframe(tbl['dataframe'], use_container_width=True)
        else:
            st.warning("No tables detected in this document.")

    # 5. Visuals
    with t5:
        st.markdown("""
            <div class="section-header">
                <div class="header-icon-box"><span class="material-symbols-rounded">cloud</span></div>
                <div class="header-text">Visual Analysis</div>
            </div>
        """, unsafe_allow_html=True)
        
        if full_text_content:
            try:
                wc = WordCloud(width=800, height=400, background_color='#0E1117', mode="RGBA", colormap='cool').generate(full_text_content)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wc, interpolation='bilinear'); ax.axis("off"); fig.patch.set_alpha(0)
                st.pyplot(fig); plt.close(fig)
            except: st.error("Word Cloud generation failed.")

    # 6. Gallery
    with t6:
        st.markdown(f"""
            <div class="section-header">
                <div class="header-icon-box"><span class="material-symbols-rounded">image</span></div>
                <div class="header-text">Gallery ({data["img_count"]})</div>
            </div>
        """, unsafe_allow_html=True)
        
        if data["img_count"] > 0:
            images = [os.path.join(data["output_dir"], "images", x) for x in os.listdir(os.path.join(data["output_dir"], "images")) if x.endswith(('png','jpg','jpeg'))]
            cols = st.columns(4)
            for i, img in enumerate(images):
                with cols[i%4]:
                    with st.container(border=True):
                        st.image(img, use_container_width=True)
                        st.caption(f"Image {i+1}")
        else:
            st.info("No images extracted.")

    # 7. Export
    with t7:
        st.markdown("""
            <div class="section-header">
                <div class="header-icon-box"><span class="material-symbols-rounded">download</span></div>
                <div class="header-text">Export</div>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            with st.container(border=True):
                st.markdown("**Plain Text**")
                st.download_button("Download .txt", full_text_content, f"{data['filename']}.txt", use_container_width=True)
        
        with c2:
            with st.container(border=True):
                st.markdown("**Structure**")
                export_struct = {"metadata": {"filename": data['filename'], "pdf_properties": pdf_meta}, "structure": struct}
                if 'tables' in export_struct['structure']: del export_struct['structure']['tables']
                st.download_button("Download .json", json.dumps(export_struct, indent=2, default=str), f"{data['filename']}_data.json", use_container_width=True)

        with c3:
            with st.container(border=True):
                st.markdown("**Images**")
                if data["img_count"] > 0 and data["zip_path"]:
                    with open(data["zip_path"], "rb") as f: st.download_button("Download .zip", f, f"{data['filename']}_imgs.zip", use_container_width=True)
                else:
                    st.button("No Images", disabled=True, use_container_width=True)
                    
        with c4:
            with st.container(border=True):
                st.markdown("**Excel Tables**")
                if tables:
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for i, tbl in enumerate(tables):
                            sheet_name = f"Table_{i+1}_Pg{tbl['page']}"
                            tbl['dataframe'].to_excel(writer, sheet_name=sheet_name, index=False)
                    output.seek(0)
                    st.download_button("Download .xlsx", output, f"{data['filename']}_tables.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                else:
                    st.button("No Tables", disabled=True, use_container_width=True)

    # --- FOOTER ---
    st.markdown("""
        <div class="footer" style="text-align:center; padding:40px 0; color:#64748b; font-size:0.8rem; border-top:1px solid rgba(255,255,255,0.05);">
            <p>PDF Extractor Pro &copy; 2024</p>
        </div>
    """, unsafe_allow_html=True)

    # 8. Persona AI (Challenge 1B-style)
    with t8:
        st.markdown(
            '''
            <div class="section-header">
                <div class="header-icon-box"><span class="material-symbols-rounded">psychology</span></div>
                <div class="header-text">Persona AI</div>
            </div>
            ''',
            unsafe_allow_html=True
        )

        st.caption("Give a persona + job-to-be-done. We'll semantically rank the most relevant pages from this PDF (offline TF-IDF).")

        colA, colB = st.columns(2)
        with colA:
            persona_name = st.text_input("Persona", value="Research Analyst", key="persona_1b")
            top_k = st.slider("Top results (pages)", min_value=3, max_value=15, value=8, step=1, key="topk_1b")
        with colB:
            job_task = st.text_area("Job-to-be-done (task)", value="Extract the most relevant insights for the persona.", height=100, key="job_1b")
            min_chars = st.slider("Minimum text per page (filter scanned/empty pages)", min_value=20, max_value=200, value=60, step=10, key="minchars_1b")

        if st.button("Run Persona AI", type="primary", use_container_width=True, key="run_1b_btn"):
            if "data" not in st.session_state or "file_path" not in st.session_state.data:
                st.error("Please initialize analysis first (click 'Initialize Analysis') so the PDF is loaded.")
            else:
                pdf_path = st.session_state.data["file_path"]
                with st.spinner("Ranking relevant pages..."):
                    try:
                        out = run_persona_intelligence(
                            pdf_path=pdf_path,
                            persona_name=persona_name,
                            job_task=job_task,
                            top_k=top_k,
                            min_chars=min_chars,
                        )
                        st.session_state["persona_1b_output"] = out
                    except Exception as e:
                        st.exception(e)

        out = st.session_state.get("persona_1b_output")
        if out:
            st.subheader("Results")
            extracted = out.get("extracted_sections", [])
            if out.get("warning"):
                st.warning(out["warning"])

            if extracted:
                for item in extracted:
                    with st.expander(
                        f"#{item.get('importance_rank')} • Page {item.get('page_number')} • score={item.get('score')}"
                    ):
                        st.write("**Title:**", item.get("section_title"))
                        # show refined text from subsection_analysis
                        match = None
                        for s in out.get("subsection_analysis", []):
                            if s.get("page_number") == item.get("page_number"):
                                match = s
                                break
                        if match:
                            st.write(match.get("refined_text", ""))

                st.download_button(
                    "Download 1B JSON",
                    data=json.dumps(out, indent=2, ensure_ascii=False),
                    file_name="challenge1b_output.json",
                    mime="application/json",
                    use_container_width=True,
                )
            else:
                st.info("No relevant sections found (or PDF text could not be extracted).")
