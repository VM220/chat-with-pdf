import streamlit as st

def display_sources(sources, message_id):
    if sources:
        with st.expander("📖 View Sources"):
            for i, source in enumerate(sources):
                unique_key = f"source_{message_id}_{i}_{hash(source.page_content[:50]) % 1000}"
                st.text_area(
                    f"Content {i+1}",
                    source.page_content[:500] + "..." if len(source.page_content) > 500 else source.page_content,
                    height=100,
                    key=unique_key
                )
                if hasattr(source, 'metadata'):
                    st.caption(f"📄 Page: {source.metadata.get('page', 'Unknown')}")
                st.markdown("---")
