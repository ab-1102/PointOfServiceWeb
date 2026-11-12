
export default function({ data }) {

    async function sendToLocal() {
        try {
            // Wait for PyWebView if it is not ready yet.
            if (!window.top.pywebview?.api?.hello) {
                await new Promise((resolve, reject) => {
                    const timeout = setTimeout(
                        () => reject(new Error("PyWebView unavailable")),
                        10000
                    );

                    window.top.addEventListener(
                        "pywebviewready",
                        () => {
                            clearTimeout(timeout);
                            resolve();
                        },
                        { once: true }
                    );
                });
            }

            const response = await window.top.pywebview.api.hello(
                data.bill
            );

            console.log(response);

        } catch (error) {
            console.error("Bridge error:", error);
        }
    }

    sendToLocal();
}
