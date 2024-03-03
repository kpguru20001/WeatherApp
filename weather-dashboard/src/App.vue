<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  darkTheme,
  type GlobalThemeOverrides,
  NConfigProvider,
  NSelect,
  NDivider,
  NInput,
  NMessageProvider,
  useMessage,
  NButton,
  createDiscreteApi,
  type ConfigProviderProps
} from 'naive-ui'
import type { SelectMixedOption } from 'naive-ui/lib/select/src/interface'
import axios from 'axios'

const configProviderPropsRef = computed<ConfigProviderProps>(() => ({
  theme: darkTheme
}))

const { message, notification, dialog, loadingBar, modal } = createDiscreteApi(
  ['message', 'dialog', 'notification', 'loadingBar', 'modal'],
  {
    configProviderProps: configProviderPropsRef
  }
)
type WeatherData = {
  location: string
  temperature: number
  humidity: number
  description: string
}
const themeOverrides: GlobalThemeOverrides = {
  common: {
    borderRadius: '6px',
    heightTiny: '32px',
    heightSmall: '36px',
    heightMedium: '40px',
    heightLarge: '46px',
    pressedColor: 'rgb(237, 237, 239)'
  },
  Button: {
    fontWeight: '500',
    paddingMedium: '0 20px',
    paddingLarge: '0 24px'
  }
}
const userName = ref('')
const locationOne = ref('')
const locationTwo = ref('')
const locationThree = ref('')

const nameToCreate = ref('')
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
        label: item.name,
        ...item
      })
    )
    console.log(namesFromServer.value)
  } catch (e) {
    console.error(e)
  } finally {
    loadingRef.value = false
  }
}
const createName = async () => {
  loadingRef.value = true
  if (!nameToCreate.value.length) {
    return
  }
  try {
    const response = await axios.post('http://127.0.0.1:8000/users/', {
      name: nameToCreate.value
    })
    userName.value = response.data.name
    message.success('User Created')
  } catch (e) {
    console.error(e)
    message.error('User Creation Failed')
  } finally {
    loadingRef.value = false
  }
}

const pincode = ref('')
const currentWeatherData = ref<WeatherData | null>(null)
const loc1WD = ref<WeatherData | null>(null)
const loc2WD = ref<WeatherData | null>(null)
const loc3WD = ref<WeatherData | null>(null)
const getWeatherData = async (pincodeWCountry: string) => {
  if (!pincodeWCountry.length) {
    return
  }
  const pincodeArr = pincodeWCountry.split(',')
  try {
    // using http://127.0.0.1:8000/weather/?zip=545&country=IN
    const response = await axios.get(`
    http://127.0.0.1:8000/weather/?zip=${pincodeArr[0]}&country=${pincodeArr[1]}`)
    console.log(response.data.current)
    console.log(response.data.location_info.display_name)
    return {
      location: response.data.location_info.display_name,
      temperature: response.data.current.temp,
      humidity: response.data.current.humidity,
      description: response.data.current.weather[0].description
    }
  } catch (e) {
    console.error(e)
    return null
  }
}
const handleWeatherSearch = async () => {
  loadingRef.value = true
  try {
    const weatherD = await getWeatherData(pincode.value)
    if (!weatherD) {
      message.error('Weather Data not found')
    } else {
      currentWeatherData.value = weatherD
      message.success('Weather Data Found')
    }
  } catch (e) {
    console.error(e)
    message.error('Weather Data not found')
  }
  loadingRef.value = false
}

watch(
  () => locationOne.value,
  async (newVal, ov) => {
    if (newVal.length && ov != newVal) {
      loc1WD.value = (await getWeatherData(newVal)) ?? null
    }
  }
)

watch(
  () => locationTwo.value,
  async (newVal, ov) => {
    if (newVal.length && ov != newVal) {
      loc2WD.value = (await getWeatherData(newVal)) ?? null
    }
  }
)

watch(
  () => locationThree.value,
  async (newVal, ov) => {
    if (newVal.length && ov != newVal) {
      loc3WD.value = (await getWeatherData(newVal)) ?? null
    }
  }
)

const updateData = async () => {
  if (userName.value.length) {
    try {
      const response = await axios.put(`http://127.0.0.1:8000/users/${userName.value}/`, {
        name: userName.value,
        locationOne: locationOne.value,
        locationTwo: locationTwo.value,
        locationThree: locationThree.value
      })
      userName.value = response.data.name
      locationOne.value = response.data.locationOne ?? ''
      locationTwo.value = response.data.locationTwo ?? ''
      locationThree.value = response.data.locationThree ?? ''
      console.log(response)
      message.success('User Updated')
    } catch (e) {
      console.error(e)
      message.error('User Updation Failed')
    } finally {
      loadingRef.value = false
    }
  }
}

const addLocation = async () => {
  switch (true) {
    case locationOne.value === '':
      locationOne.value = pincode.value
      break
    case locationTwo.value === '':
      locationTwo.value = pincode.value
      break
    case locationThree.value === '':
      locationThree.value = pincode.value
      break
    default:
      message.error('You can only track 3 locations')
  }
  updateData()
}
</script>

<template>
  <n-config-provider :theme="darkTheme" :theme-overrides="themeOverrides">
    <n-message-provider>
      <div class="px-24 pt-4 container mx-auto">
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
                <p class="pt-4 text-base">Search your name</p>
                <n-select
                  :value="userName"
                  filterable
                  tag
                  placeholder="Search User Name"
                  :options="namesFromServer"
                  :loading="loadingRef"
                  remote
                  @search="handleSearch"
                  @update:value="
                    (value: any, option: any) => {
                      ;(userName = value),
                        (locationOne = option['locationOne'] ?? ''),
                        (locationTwo = option['locationTwo'] ?? ''),
                        (locationThree = option['locationThree'] ?? '')
                    }
                  "
                />
                <n-divider>or</n-divider>
                <n-input v-model:value="nameToCreate"></n-input>
                <div class="card-actions justify-end pt-4">
                  <button class="btn" @click="createName">Create</button>
                </div>
              </div>
            </div>
          </div>
          <!-- The Dashboard with Name set -->
          <div v-else>
            <div class="px-6 prose">
              <h2>Welcome {{ userName }}!</h2>
              <p>
                Here is your weather data. Please use search to load weather data from specific pin
              </p>
            </div>
            <div class="flex flex-row justify-between items-start">
              <div class="w-3/5 flex flex-col gap-5">
                <div class="card bg-base-100 shadow-xl">
                  <div class="card-body">
                    <h2 class="card-title">Search Weather Data</h2>
                    <n-input v-model:value="pincode"></n-input>
                    <div class="card-actions justify-end pt-4">
                      <button
                        class="btn"
                        :class="{
                          'btn-disabled': loadingRef
                        }"
                        @click="handleWeatherSearch"
                      >
                        <span v-if="loadingRef" class="loading loading-spinner"></span>Search
                      </button>
                    </div>
                  </div>
                </div>
                <div v-if="currentWeatherData" class="card bg-base-100 shadow-xl">
                  <div class="card-body">
                    <h2 class="card-title">Current Weather Data</h2>
                    <p>Location: {{ currentWeatherData.location }}</p>
                    <p>Temperature: {{ currentWeatherData.temperature }} C</p>
                    <p>Humidity: {{ currentWeatherData.humidity }} %</p>
                    <p>Description: {{ currentWeatherData.description }}</p>
                    <div class="card-actions justify-end">
                      <button class="btn btn-primary" @click="addLocation">Track Weather</button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="w-2/5 flex flex-col gap-4">
                <div
                  class="card w-full bg-primary text-primary-content"
                  v-if="locationOne !== '' && loc1WD"
                >
                  <div class="card-body">
                    <h2 class="card-title">Your Weather Data</h2>
                    <p>Weather data will be displayed here</p>
                    <p>Pincode: {{ locationOne }}</p>
                    <p>Location: {{ loc1WD.location }}</p>
                    <p>Temperature: {{ loc1WD.temperature }} C</p>
                    <p>Humidity: {{ loc1WD.humidity }} %</p>
                    <p>Description: {{ loc1WD.description }}</p>
                    <div class="card-actions justify-end">
                      <button
                        class="btn btn-outline btn-sm"
                        @click="
                          () => {
                            locationOne = ''
                            updateData()
                          }
                        "
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
                <div
                  class="card w-full bg-primary text-primary-content"
                  v-if="locationTwo !== '' && loc2WD"
                >
                  <div class="card-body">
                    <h2 class="card-title">Your Weather Data</h2>
                    <p>Weather data will be displayed here</p>
                    <p>Pincode: {{ locationTwo }}</p>
                    <p>Location: {{ loc2WD.location }}</p>
                    <p>Temperature: {{ loc2WD.temperature }} C</p>
                    <p>Humidity: {{ loc2WD.humidity }} %</p>
                    <p>Description: {{ loc2WD.description }}</p>
                    <div class="card-actions justify-end">
                      <button
                        class="btn btn-outline btn-sm"
                        @click="
                          () => {
                            locationTwo = ''
                            updateData()
                          }
                        "
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
                <div
                  class="card w-full bg-primary text-primary-content"
                  v-if="locationThree !== '' && loc3WD"
                >
                  <div class="card-body">
                    <h2 class="card-title">Your Weather Data</h2>
                    <p>Weather data will be displayed here</p>
                    <p>Pincode: {{ locationThree }}</p>
                    <p>Location: {{ loc3WD.location }}</p>
                    <p>Temperature: {{ loc3WD.temperature }} C</p>
                    <p>Humidity: {{ loc3WD.humidity }} %</p>
                    <p>Description: {{ loc3WD.description }}</p>
                    <div class="card-actions justify-end">
                      <button
                        class="btn btn-outline btn-sm"
                        @click="
                          () => {
                            locationThree = ''
                            updateData()
                          }
                        "
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </n-message-provider>
  </n-config-provider>
</template>

<style></style>
