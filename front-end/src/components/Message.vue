<template>
  <div class="message">
    <div class="meta">
      <span class="name">{{message.author}}</span>
      <span class="time">{{message.time | moment('YYYY/MM/DD HH:MM:SS')}}</span>
    </div>
    <div class="msg">{{message.content}}</div>
  </div>
</template>

<script>
export default {
  props: {
    message: {
      type: Object
    }
  }
}
</script>

<style lang="scss" scoped>
.message {
  background: hsla(209, 100%, 41%, 1);
  color: #fff;
  padding: .8em;
  border-radius: .4em;
  margin-bottom: 1em;

  .meta {
    margin-bottom: .2em;
    clear: both;
    font-size: .8em;

    .name {
      font-weight: bold;
    }

    .time {
      color: #dedede;
      float: right;
    }
  }
}
</style>
