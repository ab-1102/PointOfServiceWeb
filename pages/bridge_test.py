
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

            async function callPython() {
                try {
                    status.textContent = "Connecting...";

                    // Wait if the PyWebView API is not ready yet.
                    if (!window.pywebview?.api) {
                        await new Promise((resolve, reject) => {
                            const timeout = setTimeout(
                                () => reject(new Error("PyWebView API unavailable")),
                                5000
                            );

                            window.addEventListener(
                                "pywebviewready",
                                () => {
                                    clearTimeout(timeout);
                                    resolve();
                                },
                                { once: true }
                            );
                        });
                    }

                    const response =
                        await window.pywebview.api.hello();

                    status.textContent = response;

                    // Send the response back to Streamlit Python.
                    setStateValue("response", response);

                } catch (error) {
                    status.textContent = error.message;
                    setStateValue("response", "ERROR: " + error.message);
                }
            }

            button.addEventListener("click", callPython);
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
