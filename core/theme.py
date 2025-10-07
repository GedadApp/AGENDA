def inject_modern_css(st):
    st.markdown("""
    <style>
      .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
      .modern-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem 1.4rem;
        border-radius: 12px;
        color: #fff;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      }
      .modern-card {
        background: #fff;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
      }
      .muted { color: #6b7280; font-size: 0.9rem; }
      .btn-row .stButton>button { width: 100%; }
      .form-row { margin-top: .4rem; }
      .legend { font-weight: 600; margin-bottom: .4rem; }
      .pill {
        display: inline-block; padding: .25rem .6rem; border-radius: 999px;
        background: #eef2ff; color: #4338ca; font-size: .8rem; margin-left: .5rem;
      }
      .table-note { font-size: .85rem; color: #6b7280; margin-top: .25rem; }
      /* Improve expander spacing */
      .streamlit-expanderHeader { font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)
