Vue.component('sub-menu', {
    props: ['menus', 'fold'],
    methods: {
        open_Tab(data) {
            window.app.openTab(data);
        }
    },
    template: `
        <div >
            <template v-for="(item,i) in menus" :key="item.eid">
               
                <el-menu-item  :index="item.eid" v-if="!item.models" @click="open_Tab(item,item.eid)">
                    <i :class="'menu-icon '+item.icon" v-if="item.icon"></i>
                    <span  v-text="item.name" id="123222" ></span>
                 </el-menu-item>
               
                <el-submenu :index="item.eid" v-else>
                    <template slot="title" >
                        <i :class="'menu-icon '+item.icon" v-if="item.icon"></i>
                        <!--  <span v-show="!fold" v-text="item.name" ></span>-->
                        <span  v-text="item.name" ></span>
                    </template>
                    <sub-menu :menus="item.views"></sub-menu>
                    <sub-menu :menus="item.models"></sub-menu>
                </el-submenu>
            </template>
        </div>
    `

});

Vue.component('multiple-menu', {
    props: ['menus', 'menuActive', 'fold'],
    template: `
     <el-menu :unique-opened="true" :default-active="menuActive" :collapse="fold" :collapse-transition="true">
        <sub-menu :menus="menus" :fold="fold"></sub-menu>
    </el-menu>
    `
});