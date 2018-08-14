# vscode 配置及代码相关规范

> 在做项目前我们需要对 IDE 进行配置，还需要一些必要的开发规范，后面协同开发的时候不至于各种凌乱，工欲善其事，必先利其器，再加上行事风格 方成大器也！！！（闲话说多了，往下看--》）

## vscode

* 插件安装

> Auto Close Tag
> Babel ES6/ES7
> Beautify
> Easy LESS 这个插件需禁用
> ESLint
> HTML CSS Support
> HTML Snippets
> Path Autocomplete
> Prettier- Code formatter
> Sublime Text Keymap and Settting Importer
> TSLint
> Vetur
> Vue 2 Snippets
> VueHelper

* vscode 设置

```javascript
    {
    "telemetry.enableTelemetry": false,
    "sublimeTextKeymap.promptV3Features": true,
    "editor.multiCursorModifier": "ctrlCmd",
    "editor.snippetSuggestions": "top",
    "editor.formatOnPaste": true,
    "workbench.startupEditor": "newUntitledFile",
    "editor.fontSize": 16,
    "extensions.ignoreRecommendations": true,
    "editor.tabSize": 2,
    "editor.formatOnSave": true,
    "editor.formatOnType": true,
    "html.format.indentInnerHtml": true,
    "html.format.indentHandlebars": true,
    "javascript.implicitProjectConfig.experimentalDecorators": true,
    "vetur.validation.template": false,
    "vetur.format.defaultFormatter.html": "js-beautify-html",
    "prettier.printWidth": 200,
    "prettier.singleQuote": true
}
```

> 基本配置就这些，其他炫酷主题及插件可根据个人喜好安装！！！

##注意事项

### 1.相关规范

* 图片文件名统一小写,遇到多个单词以-横线连接，例如：logo.png,i-phone.png
* CSS 命名
  > 类名使用小写字母，以中划线分隔
  > id 采用驼峰式命名
  > less 中的变量、函数采用小写字母，以中划线分隔

例如：

```css
/* class */
.element-content {
  ...;
}
/* id */
#myDialog {
  ...;
}
/* 变量 */
@color-black: #000;

/* 函数 */
.button-color(@color; @background; @border) {
  ...;
}
```

* js 规范

> 字符串最外层统一使用单引号。例如：

```js
var z = '<div id="test"></div>';
```

> 标准变量采用驼峰式命名
> 'ID'在变量名中全大写
> 'URL'在变量名中全大写常量全大写，用下划线连接构造函数，大写第一个字母
> jquery 对象必须以'$'开头命名

```js
var thisIsMyName;
var goodID; //id全大写
var reportURL; //url全大写
var MAX_COUNT = 10;
function Person(name) {
  this.name = name;
}
// not good
var body = $('body');
// good
var $body = $('body');
```

> 永远不要直接使用 undefined 进行变量判断；使用 typeof 和字符串'undefined'对变量进行判断。

```javascript
// not good
if (person === undefined) {
    ...
}
// good
if (typeof person === 'undefined') {
    ...
}
```

### 2.SVN 提交首次提交 在 svn 里面需要忽略 node_modules 文件夹

> 再次提交时，先拉取线上代码，合并代码，解决冲突 再提交 务必写上注释！！！

    暂时先写这么多，后面会再补充！！！
