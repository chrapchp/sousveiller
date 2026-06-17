import { LMap, LTileLayer, LCircleMarker, LPopup } from '@vue-leaflet/vue-leaflet'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.component('LMap', LMap)
  nuxtApp.vueApp.component('LTileLayer', LTileLayer)
  nuxtApp.vueApp.component('LCircleMarker', LCircleMarker)
  nuxtApp.vueApp.component('LPopup', LPopup)
})
