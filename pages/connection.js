export default function({ data }) {

    console.log("Received data:", data);

    async function sendToLocal() {
        try {
            const billData = data.bill_data;

            console.log("Bill data:", billData);
            console.log("Bill data type:", typeof billData);

            const json = JSON.stringify(billData);

            console.log("JSON payload:", json);

            const payload = JSON.parse(json);

            const response =
                await window.top.pywebview.api.print_bill(payload);

            console.log("Python response:", response);

        } catch (error) {
            console.error("Bridge error:", error);
        }
    }

    sendToLocal();
}