<template>
  <div class="row bg-white shadow mt-n5 border-radius-lg pb-4 p-3 position-relative w-75 mx-auto">
    <div class="d-flex flex-row align-content-center">
      <div class="d-flex align-items-center border rounded-pill me-2 w-75">
        <div v-for="(item, index) in elementsSearch" :key="item"
             class="badge rounded-pill choices-dark ms-2 user-select-none"
             style="height: 24px;" :id="'element-to-search' + index">
          {{ item }}
          <i class="fa fa-times border-start border-2 ms-1 ps-1" role="button"
             @click="delElementToSearch({id: 'element-to-search' + index, value: item})"></i>
        </div>
      </div>
      <div class="d-flex align-items-center w-25">
        <button type="button" class="btn bg-gradient-primary w-100 mb-0">Rechercher</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
// store
import { storeToRefs } from 'pinia'
import { useAllStore } from '@/stores/all'

const { events, place } = storeToRefs(useAllStore())
let elementsSearch = ref([])

// réceptione le données de recherche
addEventListener('ElementToSearch', (event) => {
  if (!elementsSearch.value.includes(event.detail.name)) {
    elementsSearch.value.push(event.detail.name)
  }
})

function delElementToSearch (data) {
  console.log('-> delElementToSearch, id =', data.id)
  let sysElement = document.querySelector('#' + data.id)
  sysElement.parentNode.removeChild(sysElement)
  elementsSearch.value = elementsSearch.value.filter((item) => item !== data.value)
}
</script>

<style>
</style>