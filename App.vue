<script setup lang="ts">
import { ref } from 'vue'
import { darkTheme, type GlobalThemeOverrides, NConfigProvider, NSelect } from 'naive-ui'
import type { SelectMixedOption } from 'naive-ui/lib/select/src/interface'
import axios from 'axios'

const themeOverrides: GlobalThemeOverrides = {
  common: {
    borderRadius: '0.5rem',
    heightLarge: '2.8rem',
  },
}
const userName = ref('')
const searchedName = ref('')
const namesFromServer = ref<SelectMixedOption[]>([])
const loadingRef = ref(false)
const handleSearch = async (query: string) => {
  if (!query.length) {
    namesFromServer.value = []
    return
  }
  loadingRef.value = true
  try {
    const response = await axios.get(`http://127.0.0.1:8000/users/search/${query}`)
    const data = (response.data ?? []) as any[]
    console.log(response)
    namesFromServer.value = data.map(
      (item: any): SelectMixedOption => ({
        value: item.name,
        label: item.name
      })
    )
    console.log(namesFromServer.value)
  } catch (e) {
    console.error(e)
  } finally {
    loadingRef.value = false
  }
}
</script>

<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides" >
    <div class="px-24 pt-4">
      <div class="navbar bg-gray-700 rounded-xl shadow-2xl">
        <button class="btn btn-ghost text-xl">Your Weather App</button>
      </div>
      <div class="pt-12">
        <div
          v-if="userName === ''"
          class="flex flex-row justify-center items-centerm max-w-4xl mx-auto"
        >
          <div class="card w-full bg-primary text-primary-content">
            <div class="card-body">
              <h2 class="card-title">Please Enter Your Name</h2>
              <p>We will use your name to fetch your weather data</p>
              <p class="pt-4 text-base">Enter your name</p>
              <n-select
                label-field="Enter Your Name"
                class="mt-1 text-red-300"
                v-model:value="searchedName"
                filterable
                placeholder="Search User Name"
                :options="namesFromServer"
                :loading="loadingRef"
                clearable
                remote
                @search="handleSearch"
                size="large"
              />
              <div class="card-actions justify-end pt-4">
                <button class="btn">Start</button>
              </div>
              {{ searchedName }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </n-config-provider>
</template>

<style></style>
