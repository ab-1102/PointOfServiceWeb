
import streamlit as st

st.title("PyWebView Bridge Test")

bridge_component = st.components.v2.component(
    name="pos_bridge_test",
    html="""
        <button id="test_button">Call Local Python</button>
        <p id="status">Waiting for interaction...</p>
    """,
    css="""
        button {
            padding: 10px 18px;
            cursor: pointer;
        }
    """,
    js="""
    
export default function({ parentElement, setStateValue }) {
    const button = parentElement.querySelector("#test_button");
    const status = parentElement.querySelector("#status");

    button.addEventListener("click", async () => {
        const diagnostics = {
            currentWindow: typeof window.pywebview,
            topWindow: typeof window.top.pywebview,
            api: typeof window.pywebview?.api,
            hello: typeof window.pywebview?.api?.hello,
            isTopWindow: window === window.top,
            url: window.location.href
        };

        status.textContent = JSON.stringify(diagnostics, null, 2);

        if (typeof window.pywebview?.api?.hello === "function") {
            try {
                const response = await window.pywebview.api.hello();
                status.textContent += "\n\nResponse: " + response;
                setStateValue("response", response);
            } catch (error) {
                status.textContent += "\n\nCall error: " + error.message;
            }
        }
    });
}
        
    """
)

result = bridge_component(
    default={"response": None},
    on_response_change=lambda: None,
    key="pos_bridge_test"
)

st.divider()
st.subheader("Response received by Streamlit Python")

st.write(result.response)
