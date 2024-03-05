
const { createApp, ref } = Vue;
createApp({
    setup() {
        const count = ref(7);
        const response = ref(null);

        function increment() {
            count.value++;
        }

        function handleDrop(event) {
            event.preventDefault();

            const file = event.dataTransfer.files[0];

            if (file) {
                uploadFile(file);
            }
        }

        async function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('http://46.101.114.188:8080',{
                    method: 'POST',
                    body: formData,
                });
                
                const data = await response.json();
                // Update the response variable to show it in the pre tag
                response.value = JSON.stringify(data, null, 2);
                console.log("value: " + response.value);
                json = JSON.parse(response.value);
                
                para = document.createElement("p");
                para.innerText = response.value;
                document.body.appendChild(para);
                
            } catch (error) {
                console.error('Error uploading file:', error);
            }
        }

        return {
            count,
            increment,
            handleDrop,
            response,
        };
    },
}).mount('#app');
