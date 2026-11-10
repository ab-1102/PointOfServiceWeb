export default function({ parentElement, setStateValue, data }) {

    if (typeof window.top.pywebview?.api?.hello === "function") {

        try {
            const response = await window.top.pywebview.api.hello(data.bill);

        } catch (error) {
            // Handle error if needed
        }
    }
}