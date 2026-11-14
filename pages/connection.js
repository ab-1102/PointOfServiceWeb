export default function({ data }) {

    console.log("Received component data:", data);
    console.log("Bill data:", data.bill_data);

    async function sendToLocal() {
        try {
            const billData = data.bill_data;

            console.log("Sending to Python:", billData);

            const response = await window.top.pywebview.api.print_bill(
                billData
            );

            console.log("Python response:", response);

        } catch (error) {
            console.error("Bridge error:", error);
        }
    }

    sendToLocal();
}