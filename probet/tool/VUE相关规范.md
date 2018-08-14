# VUE相关规范

---

> 在我们团队协作的时候，代码往往会参差不齐，五花八门，看得我们眼花缭乱。有些逻辑理解起来确实很费解，在此问题上，就衍生出了这篇小规范，请往下看，往里走！！！

## 标签问题
```html
 <div class="detail-xxx">
  <span>1</span>
  <span>2</span>
  <span>3</span>
  <span>4</span>
</div>
```

> 问题点：

 1. 尽量遵循HTML标准和语义，但是不应该以浪费实用性作为代价；
任何时候都要用尽量小的复杂度和尽量少的标签来解决问题
 2. 标签不要留空，尽量加上必要的class进行说明

>  方案：

 例如：
```html
 <div class="detail-xxx">
   <span class="num">1</span>
 </div>
```

## 冗余问题

 1. JS冗余
    代码就不贴了，主要是方法、类、变量的冗余，能抽取的都把它抽取出来。
 
 2. CSS冗余
```less
    .module-a{
        .a{
        xx:xxx
        }
    }
    .modulea-b{
        .a{
        xx:xxx
        }
    }
    ...module-n{
    }
```
很多时候我们会定义一些相同的样式文件，一个模块是这样，多个模块就写了多个重复的东西。这里我们需要提取这部分内容，某个模块有不同的地方，然后再针对它写相应的样式。具体的做法，less官网有更详细的说明：
[http://lesscss.cn/features/][1]

> 方案：

```less
    .a{
        xx:xxx
    }
    .module-a{
        //如果模块A里面样式有差异，只需要改这块的内容
        .a{
         xx:xx2
        }
    }
```

3. 模版DOM冗余
```html
 <div class="modele-a">
  <div class="detail-xxx">
      <span>1</span>
      <span>2</span>
      <span>3</span>
      <span>4</span>
 </div>
 </div>
 <div class="modele-b">
  <div class="detail-xxx">
      <span>1</span>
      <span>2</span>
      <span>3</span>
      <span>4</span>
 </div>
 </div>
```
发现没有，冗余的很明显，我们在写vue的时候，能提组件的，尽量提取。方便自己，也方便团队的维护，你不是一个人在战斗，战壕里还有其他兄弟。

> 方案：

```html
<template>
    <div class="xxxxxx">
     <div class="detail-xxx">
          <span>1</span>
          <span>2</span>
          <span>3</span>
          <span>4</span>
     </div>
    </div> 
</template>
.....
```
## float问题
float问题很严重，用了还不清理浮动，跟耍流氓似的。玩了还不给钱！！不知道如何布局，可以搜罗下大神的博客，以及CSS的官方文档说明，学习一下总归没坏处。简单列了几个，自己可以在网上搜罗。。。
[http://zh.learnlayout.com/][2]
[https://segmentfault.com/a/1190000011358507#articleHeader8][3]
[https://www.cnblogs.com/bergwhite/p/6417800.html][4]
## img问题
这是一个关于static/assets的问题，总是不知道该放哪儿。
assests放置的是组件的资源
static放置的是非组件的资源

> 比如
static下的文件资源作为src路径传入组件中，文件的path是可以被解析了，而assets则不行。

## vuex问题
目前我们只用到了state,action,而且action里面只有axios的一些方法请求，并未做其他操作，显得vuex作用不是很大。请认真阅读一下文档内容！！！
[https://vuex.vuejs.org/zh/][5]
[http://www.shouce.ren/api/view/a/11738][6]

## DOM/逻辑混搭
```html
<div class="menu-box">
  <i class="match-state end" v-if="it.iMatchState===1">停止下注</i>
  <i class="match-state start" v-if="it.iMatchState===2">比赛中</i>
  <i class="match-state end" v-if="it.iMatchState===3">已结束</i>
  <i class="match-state end" v-if="it.iMatchState===4">赛事被官方取消</i>
  <i class="match-state end" v-if="it.iMatchState===5">后台主动关闭</i>
</div>          
```
什么鬼？在DOM上面写一大堆逻辑处理在里面，不推荐这种做法。逻辑处理应该在返回数据后，就应该处理好。DOM层只做数据渲染。

## css控制
```html
 <span class="second">
  <img v-if="item.type==1" src="static/images/first-blood.png" />
  <img v-if="item.type==2" src="static/images/kills.png" />
  <img v-if="item.type==3" src="static/images/kills.png" />
</span>
```
像这种形式，完全可以交给css去控制，直接控制class 效果也是一样，呈现形式不是更好？
> 方案：
```html
 <span class="second">
 <i :class="['icon',item.className]"></i>
</span>
```

## vuex mutations命名问题
```js
//登录信息
['user/login'](state, res) {
  state.userInfo = res;
},
或者
['USER_LOGIN'](state, res) {
  state.userInfo = res;
},
```
这两种皆可以，用模块名+方法名命名，能区分清楚调用的是那一块就OK！

## 注释问题
```js
if (condition) {
    // if you made it here, then all security checks passed
    allowed();
}
var zhangsan = 'zhangsan'; // one space after code
```
**单行注释:**

> 双斜线后，必须跟一个空格； 缩进与下一行代码保持一致；
可位于一个代码行的末尾，与代码间隔一个空格。

```js
/*
 * one space after '*'
 */
function foo(a, b, c, d, g, j) {
    ...
}
```
**多行注释：**

> 最少三行, '*'后跟一个空格，具体参照右边的写法；

应用场景：

 - 难于理解的代码段
 - 可能存在错误的代码段
 - 浏览器特殊的HACK代码
 - 业务逻辑强相关的代码
 - 函数、类

##结尾
暂时先写这么多，闲暇之余，多学习，提升自我，提升整体战斗力，文中有疑问欢迎斧正！！！

  [1]: http://lesscss.cn/features/
  [2]: http://zh.learnlayout.com/
  [3]: https://segmentfault.com/a/1190000011358507#articleHeader8
  [4]: https://www.cnblogs.com/bergwhite/p/6417800.html
  [5]: https://vuex.vuejs.org/zh/
  [6]: http://www.shouce.ren/api/view/a/11738