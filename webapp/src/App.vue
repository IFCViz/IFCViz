<script>
import FileUploader from '@/components/FileUploader.vue'

export default {
  data() {
    return {}
  },
  name: 'App',
  components: {
    FileUploader
  }
}
</script>
<template>
  <FileUploader />
</template>
<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
