<template>
  <div class="group" :class="{selected: selected}">
    <span v-for="name in member">{{name}} </span>
  </div>
</template>

<script>
export default {
  props: {
    member: {
      type: Array,
      default () {
        return ['No', 'Mem', 'Ber']
      }
    },
    selected: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style lang="scss" scoped>
.group {
  background-color: hsl(169, 100%, 41%);
  padding: .5em;
  margin: .3em 0;
  border-radius: .4em;
  cursor: pointer;
  color: #333;

  span {
    display: inline-block;
    padding: 0 .2em;
  }
}

.selected {
  background-color: hsl(187, 90%, 64%);
}
</style>
