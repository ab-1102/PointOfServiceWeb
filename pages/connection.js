export default function({ data }) {

    console.log("1. COMPONENT EXECUTED");
    console.log("2. RECEIVED DATA:", data);

    console.log("3. WINDOW:", window);
    console.log("4. TOP WINDOW:", window.top);

    try {
        console.log("5. PYWEBVIEW:", window.top.pywebview);

        console.log(
            "6. PYWEBVIEW API:",
            window.top.pywebview?.api
        );

    } catch (error) {
        console.error("ACCESS ERROR:", error);
    }

    async function sendToLocal() {
        try {
            await window.top.pywebview.api.print_bill(
                data.bill_data
            );

            console.log("7. CALL SUCCESSFUL");

        } catch (error) {
            console.error("CALL FAILED:", error);
        }
    }

    sendToLocal();
}