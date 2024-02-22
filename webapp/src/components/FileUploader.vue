<script>
export default {
    data() {
        return {
        fileexist: false
        }
    },
    name: "FileUploader",
    methods: {
        updatefileuploadstate(event) {
            if (event.target.files.length == 0) {
                return;
            }
            this.fileexist = true;
        }
    },
}
</script>

<template>
    <div class="fileuploader">
        <input @change="updatefileuploadstate($event)" type="file"/>
        <button v-if="fileexist">Upload file</button>
    </div>
</template>

<style>
.fileuploader {
    margin-left: auto;
    margin-right: auto;
    width: 50%;
    border: 2px solid black;

    display: flex;
    flex-direction: column;
    align-content: center;
}

.fileuploader > input[type="file"] {
    color: blue;
}
</style>