<template>
  <div>
    <div class="container">
      <div class="col-md-3 col-lg-2 col-lg-offset-1">
        <h2>Group List</h2>

        <ul v-if="groups.length > 0">
          <li v-for="group in groups" @click="show(group)">
            <group-item :member="group.split(/,/g)" :selected="group == display_group"></group-item>
          </li>
        </ul>
        <p v-else>No Groups Data</p>
      </div>

      <div class="col-md-9 col-lg-8">
        <h2>Message</h2>

        <div class="messages">
          <template v-if="display_group && messages[display_group]">
            <message v-for="msg in messages[display_group]" :message="msg"></message>
          </template>
          <p v-else>No message or loading...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import request from 'superagent'
import GroupItem from 'components/GroupItem'
import Message from 'components/Message'

const API_BASE = 'http://localhost:8787'

export default {
  components: { GroupItem, Message },
  created () {
    request.get(API_BASE + '/fetch').query({type: 'groups'}).end((err, res) => {
      if (err) {
        console.log('err')
      } else {
        const data = JSON.parse(res.text)
        const groups = data.groups || []
        this.groups = groups
      }
    })
  },
  data () {
    return {
      groups: [],
      messages: {},
      display_group: null
    }
  },
  methods: {
    show (group) {
      request.get(API_BASE + '/fetch').query({type: 'message', 'group': group}).end((err, res) => {
        if (err) {
          console.log(err)
        } else {
          const data = JSON.parse(res.text)
          const messages = data.messages || []
          this.messages[group] = messages
          this.display_group = group
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
ul {
  padding: 0;

  li {
    list-style: none;
    display: block;
  }
}
</style>
