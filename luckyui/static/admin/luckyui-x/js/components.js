// 通知抽屉
Vue.component('notify-drawer', {
    props: ['is_notify_drawer', 'doctor_id'],
    data() {
        return {
            notify_list: null
        }
    },
    mounted() {
        this.load_notify_list()
    },

    methods: {
        click_notify(notify) {
            console.log('点击了', notify)
        },
        load_notify_list() {
        },
        close() {
            this.$emit('close')
        },
        jump_notify_list() {
            // window.open('doctor/doctornotify')
            // window.location.href ='admin/doctor/doctornotify'

            let urls = {
                addUrl: "/admin/doctor/doctornotify/add/",
                eid: 1021,
                url: "/admin/doctor/doctornotify/",
                name: "医生通知",
                icon: "fas fa-user-md"
            }
            window.app.openTab(urls);
        }

    },

    template: `
    
       <el-drawer
              class="notify-drawer"
              title="消息通知中心"
              :visible="is_notify_drawer"
              size="30%"
              @close="close"
              :show-close = "false"
              :modal = "false"
             >
              <div class="notify-head">
                  <div v-for="(notify, index) in notify_list" :key="index" @click="click_notify(notify)" class="text-item">
                     <div class="notify-left">
                         <div class="notify-title">{{notify.notify_type_str}}</div>
                         <div class="notify-content" :style="notify.is_read==false?'color: #030229':'color:#999999'"> {{notify.content}} </div>
                    </div>
                    <div class="notify-right">{{notify.create_date}}</div> 
                  </div>
                  <div class="text-more" @click="jump_notify_list()">----点击加载更多-----
                  </div>
              </div>
     
             <div class="notify-footer" style="position: absolute;bottom: 5px;right: 10px;">
                      <el-button type="text">全部已读</el-button>
                 </div>
        </el-drawer>
  
        `
})
