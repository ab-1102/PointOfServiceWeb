export default function({ data }) {

    console.log("COMPONENT EXECUTED");

    async function sendToLocal() {
        try {
            const payload = data.bill_json;

            console.log("JSON PAYLOAD:", payload);
            console.log("PAYLOAD TYPE:", typeof payload);

            const response =
                await window.top.pywebview.api.print_bill(payload);

            console.log("PYTHON RESPONSE:", response);

        } catch (error) {
            console.error("BRIDGE ERROR:", error);
        }
    }

    sendToLocal();
}