function recomm(search_value){
    var value = search_value;   //搜索的关键词，需要ajax传递的参数
    //this.search_value=value;
    if(value.replace(/(^\s*)|(\s*$)/g,'')==""){ return; }//值为空，退出
    jQuery.noConflict();
            
            jQuery.ajax({
                url:"/search?phrase="+value, //修改这个url，并带参数 
                dataType:'json',  
                data:'',  
                jsonp:'callback',   
                //async: false
                type:'GET',
               // dataType:'json',
                    success : function(result) {  
                        if(result){
                            tableNode=document.createElement("table");//获得对象 
                            tableNode.setAttribute("id","table");
                            var div_index=0;//记录创建的DIV的索引
                            //console.log(result)    
        
                            var dataObj=eval(result);  
                            
                            var table_index=0;
                            for(var x=0;x<3;x++){ 
                                var trNode=tableNode.insertRow(); 
                                for(var y=0;y<3;y++){
                                    var tdNode=trNode.insertCell(); 
                                    if(dataObj.length > table_index)
                                    {
                                        tdNode.innerHTML=dataObj[table_index].name+"<a href=\"javascript:test('"+dataObj[table_index].name+"')\">";//加一个超链接 但是还不知道链接咋写 
                                        table_index++; 
                                        //break;
                                    }        
                                } 
                            } 
                            document.getElementById("recommend").appendChild(tableNode);//添加到那个位置 
                            
                        }
                    },
                    error : function(XMLHttpRequest, textStatus, errorThrown) { 
                        console.log(errorThrown)   
                    } 
            });
    
    
    
}
