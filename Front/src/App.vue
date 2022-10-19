<template>
  <Loading v-if="testLoading() === true"/>
  <p v-if="error !== null" class="text-dark">{{ error }}</p>
  <router-view/>
</template>

<script setup>
// composants
import Loading from '@/components/Loading.vue'

// store
import {storeToRefs} from 'pinia'
import {useAllStore} from '@/stores/all'

// font monserrat
import '@/assets/css/font_Montserrat_Open_Sans_Condensed.css'

// Nucleo Icons (ui)
import '@/assets/css/nucleo-icons.css'

// Font Awesome Free 5.15.4 MIT License
import '@/assets/js/kit-fontawesome-42d5adcbca.js'

// bootstrap (ui)
import '@/assets/css/bootstrap-5.0.2/bootstrap.min.css'
import '@/assets/js/bootstrap-5.0.2/bootstrap.bundle.min.js'

// perfect-scrollbar
import '@/assets/css/perfect-scrollbar.css'
import '@/assets/js/perfect-scrollbar/perfect-scrollbar.min.js'

// css (ui)
import '@/assets/css/now-design-system-pro.min.css'
import '@/assets/js/now-design-system-pro.js'

const {loading, error} = storeToRefs(useAllStore())

// return loading value and lock/unlock scroll
function testLoading() {
  if (loading.value === true) {
    document.body.style.userSelect = "none"
    return true
  } else {
    document.body.style.userSelect = "auto"
    return false
  }
}

// this.$route.params
</script>

<style>
body {
  overflow-x: hidden;
  overflow-y: auto;
}
</style>