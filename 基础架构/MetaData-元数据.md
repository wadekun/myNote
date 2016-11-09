# 元数据 (MetaData)
摘抄自阮一峰的博客[元数据（MetaData）](http://www.ruanyifeng.com/blog/2007/03/metadata.html)

> 元数据是用来描述数据的数据。  

举个例子：  
契科夫的小说《套中人》中的一段。描述一个叫瓦莲子卡的女子：
> （她）年纪已经不轻，三十岁上下，个子高挑，身材匀称，黑黑的眉毛，红红的脸蛋－－一句话，不是姑娘，而是果冻，她那样活跃，吵吵嚷嚷，不停地哼着小俄罗斯的抒情歌曲，高声大笑，动不动就发出一连串响亮的笑声：哈，哈，哈！

这段话里提供了以下几个信息：年龄(三十岁上下)、身高(个子高挑)、相貌(身材匀称，嘿嘿的眉毛，哄哄的脸蛋)、性格(活跃，吵吵嚷嚷，不停的哼着小俄罗斯的饿抒情歌曲，高声大笑)。有了这些信息，我们就可以大致想象出瓦连卡是个什么样的人。推而广之，只要提供这几类的信息，我们也可以推测出其他人的样子。

这个例子中的“年龄”、“身高”、“相貌”、“性格”，就是元数据，因为他们是用来描述具体 数据/信息 的 数据/信息。

日常生活中，元数据无处不在。

再例如：    
喜欢摄影的人应该知道，每张数码照片都包含EXIF信息。它是一种用来描述数码图片的元数据。按照Exif2.1标准，其中主要包含这样一些信息：  

      Image Description 图像描述、来源. 指生成图像的工具
      Artist 作者 有些相机可以输入使用者的名字
      Make 生产者 指产品生产厂家
      Model 型号 指设备型号
      Orientation方向 有的相机支持，有的不支持
      XResolution/YResolution X/Y方向分辨率 本栏目已有专门条目解释此问题。
      ResolutionUnit分辨率单位 一般为PPI
      Software软件 显示固件Firmware版本
      DateTime日期和时间
      YCbCrPositioning 色相定位
      ExifOffsetExif信息位置，定义Exif在信息在文件中的写入，有些软件不显示。
      ExposureTime 曝光时间 即快门速度
      FNumber光圈系数
      ExposureProgram曝光程序 指程序式自动曝光的设置，各相机不同,可能是Sutter Priority（快门优先）、Aperture Priority（快门优先）等等。
      ISO speed ratings感光度
      ExifVersionExif版本
      DateTimeOriginal创建时间
      DateTimeDigitized数字化时间
      ComponentsConfiguration图像构造（多指色彩组合方案）
      CompressedBitsPerPixel(BPP)压缩时每像素色彩位 指压缩程度
      ExposureBiasValue曝光补偿。
      MaxApertureValue最大光圈
      MeteringMode测光方式， 平均式测光、中央重点测光、点测光等。
      Lightsource光源 指白平衡设置
      Flash是否使用闪光灯。
      FocalLength焦距，一般显示镜头物理焦距，有些软件可以定义一个系数，从而显示相当于35mm相机的焦距 MakerNote(User Comment)作者标记、说明、记录
      FlashPixVersionFlashPix版本 （个别机型支持）
      ColorSpace色域、色彩空间
      ExifImageWidth(Pixel X Dimension)图像宽度 指横向像素数
      ExifImageLength(Pixel Y Dimension)图像高度 指纵向像素数
      Interoperability IFD通用性扩展项定义指针 和TIFF文件相关，具体含义不详
      FileSource源文件 Compression压缩比。

再例如;
在电影数据库IMDB上可以查到每一部电影的信息。[IMDB](http://www.imdb.com/)本身也定义了一套元数据，用来描述每一部电影。下面是它的一级元数据，每一级下面又列出了二级元数据，总共加起来，可以从100多个方面刻画一部电影：

> Cast and Crew（演职人员）、Company Credits（相关公司）、Basic Data（基本情况）、Plot & Quotes（情节和引语）、Fun Stuff（趣味信息）、Links to Other Sites（外部链接）、Box Office and Business（票房和商业开发）、Technical Info（技术信息）、Literature（书面内容）、Other Data（其他信息）。

元数据最大的好处就是：它是信息的描述和分类可以实现格式化，从而为机器处理创造了可能。
