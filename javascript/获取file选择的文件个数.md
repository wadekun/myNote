例如一个file input : `<input type="file" name="myFile" id="myFile">`;获取该input选择的文件个数。

http://stackoverflow.com/questions/1601455/how-to-check-file-input-size-with-jquery
* 原生js

```
// 获取到file控件
var file = document.getElementById("myFile");
// 已选择的文件数组
var filesSelected = file.files;
// 文件数组的长度
var length = filesSelected.length;

// 当然，一句话就可以搞定的
var length = document.getElementById("myFile").files.length;
```

* jQuery

```
var length = $("#myFile").files.length;
```
