<template>
  <v-app>
    <Navbar />
    
    <v-main>
      <router-view />
    </v-main>
    
    <v-footer app color="surface" class="text-center">
      <div class="px-4 py-2 text-center w-100">
        &copy; {{ new Date().getFullYear() }} IOU Data
      </div>
    </v-footer>
  </v-app>
</template>

<script setup>
import Navbar from '@/components/navbar.vue'
</script>
