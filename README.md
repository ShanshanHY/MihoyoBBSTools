# 米游社辅助签到-S

基于 Python3 的米游社辅助签到项目

禁止大范围宣传本项目，谢谢配合

也请不要滥用本项目(

本项目米游币部分参考 [XiaoMiku01/miyoubiAuto](https://github.com/XiaoMiku01/miyoubiAuto) 进行编写

本项目为 [Womsxd/MihoyoBBSTools](https://github.com/Womsxd/MihoyoBBSTools) 下的一个分支，增加了一些有用但没有什么用却又有点用处的小功能
（因本人目前只玩原神，所以大多更新与原神相关）

~~你问我为什么是S？我也不知道啊～~~

- 此项目的用途

  在[原项目](https://github.com/Womsxd/MihoyoBBSTools)的基础上添加一些小功能


## 小功能列表

- Captcha 人机验证   ***（人力识别，付费服务，使用前请三思）***
- 留影叙佳期   （~~胡桃，你别走，没有你我可怎么活啊！~~）
- 云原神token自动获取   （~~不会逆向，不懂java还看不懂smail，简直要命~~）
- 云原神自动确认签到 （~~烦死了！几天不打开云原神就被签到信息刷屏，烦死了！~~)
- 更多功能，正在摆烂中 （~~哎嘿~~）
## 如何使用程序

### [部署方法（点击查看）](/SETUP.md)

### 获取米游社 Cookie

1. 打开你的浏览器,进入**无痕/隐身模式**

2. 由于米哈游修改了 bbs 可以获取的 Cookie，导致一次获取的 Cookie 缺失，所以需要增加步骤

3. 打开`https://www.miyoushe.com/ys/`并进行登入操作

4. 按下键盘上的`F12`或右键检查,打开开发者工具,点击`Source`或`源代码`

5. 键盘按下`Ctrl+F8`或点击停用断点按钮，点击` ▌▶`解除暂停

6. 点击`NetWork`或`网络`，在`Filter`或`筛选器`里粘贴 `getUserGameUnreadCount`，同时选择`Fetch/XHR`

7. 点击一条捕获到的结果，往下拉，找到`Cookie:`

8. 从`cookie_token_v2`开始复制到结尾

   ```text
   示例:
   cookie_token_v2=xxx; account_mid_v2=xxx; ltoken_v2=xxx; ltmid_v2=xxx;
   ```

9. 将此处的复制到的 Cookie 先粘贴到 config 文件的 Cookie 处，如果末尾没有`;空格`请手动补上

10. 打开`http://user.mihoyo.com/`并进行登入操作

11. 按下键盘上的`F12`或右键检查,打开开发者工具,点击 Console

12. 输入

```javascript
var cookie=document.cookie;var ask=confirm('Cookie:'+cookie+'\n\nDo you want to copy the cookie to the clipboard?');if(ask==true){copy(cookie);msg=cookie}else{msg='Cancel'}
```

回车执行，并在确认无误后点击确定。

13. 将本次获取到的 Cookie 粘贴到之前获取到的 Cookie 后面

14. **此时 Cookie 已经获取完毕了**

### 获取设备 UA

1. 使用常用的移动端设备访问 `https://www.ip138.com/useragent/`

2. 复制网页内容中的 `客户端获取的UserAgent`

3. 替换配置文件中 `useragent` 的原始内容

### Captcha 人机验证

本项目为个人修改版本，使用[2Captcha](https://2captcha.com/)进行验证码识别

**注意！由于使用了第三方 Captcha 识别服务，该功能将会收取一定的费用**

**请仔细斟酌后决定是否使用该功能！不要本末倒置！**

具体使用方法请查看[这里](/CAPTCHA.md)


## 使用的第三方库

requests: [github](https://github.com/psf/requests) [pypi](https://pypi.org/project/requests/) (当 httpx 无法使用时使用)

httpx: [github](https://github.com/encode/httpx) [pypi](https://pypi.org/project/httpx/)

crontab: [github](https://github.com/josiahcarlson/parse-crontab) [pypi](https://pypi.org/project/crontab/)

PyYAML: [github](https://github.com/yaml/pyyaml) [pypi](https://pypi.org/project/PyYAML/)

## 关于使用 Github Actions 运行

本项目**不支持**也**不推荐**使用`Github Actions`来每日自动执行！

也**不会**处理使用`Github Actions`执行有关的 issues！

推荐使用 阿里云/腾讯云 的云函数来进行每日自动执行脚本。

## Stargazers over time

想什么呢！这分支可是一个Star都没有的！
<!-- [![Stargazers over time](https://starchart.cc/ShanshanHY/MihoyoBBSTools-S.svg)](https://starchart.cc/ShanshanHY/MihoyoBBSTools-S) -->

## License

[MIT License](https://github.com/ShanshanHY/MihoyoBBSTools-S/blob/master/LICENSE)

## 鸣谢

[JetBrains](https://jb.gg/OpenSource)

[VSCode](https://code.visualstudio.com/)
