//多张图片上传
async function uploadimg(data) {
  var app = getApp()
  var imgurln=[]	
  var that = this
  
  i = data.i ? data.i : 0,  //当前上传的哪张图片
  success = data.success ? data.success : 0,  //上传成功的个数
  fail = data.fail ? data.fail : 0;  //上传失败的个数
  await uni.uploadFile({
		url: data.url, //从调用页面传入 -- url: 'http://127.0.0.1:3000/' 后端接口地址
		filePath: data.path[i], //从调用页面传入 --path: imgbox, 选取图片的地址数组  
		name: 'img', //文件名称可以自定义，要与后端配对使用：app.post('/',upload.single('img'),function(req,res,next)
		formData: {  //这里是上传图片时一起上传的数据
			// user: data.user,
			// memo: data.text   //从调用页面传入 -- text:text1 文本框内容  
		},

		success: (resp) => {
			success++;//图片上传成功，图片上传成功的变量+1
			//console.log(resp.data) //在调试窗口显示后端返回的图片名称      
			imgurln = imgurln.concat(app.globalData.url + resp.data); //以图片名称拼接成网址，并追加到数组imgurln
		},

		fail: (res) => {  //失败
			fail++;//图片上传失败，图片上传失败的变量+1
			console.log('fail:' + i + "fail:" + fail);
		},

		complete: () => { //不论成功、失败都执行		
			i++; //这个图片执行完上传后，开始上传下一张
			if (i == data.path.length) {   //当图片传完时，停止调用				
				console.log('1>'+app.globalData.url);       
				console.log('执行完毕');
				console.log('成功：' + success + " 失败：" + fail);
			} else { //若图片还没有传完，则继续调用函数
				//console.log(i);
				data.i = i;
				data.success = success;
				data.fail = fail;
				that.uploadimg(data);
			}
		}
    });
}

module.exports.uploadimg = uploadimg; //把uploadimg函数暴露，才能在其它js文件引用此函数。 
