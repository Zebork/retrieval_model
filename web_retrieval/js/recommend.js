function recomm(search_value){
    var value = search_value;   //�����Ĺؼ��ʣ���Ҫajax���ݵĲ���
    //this.search_value=value;
    if(value.replace(/(^\s*)|(\s*$)/g,'')==""){ return; }//ֵΪ�գ��˳�
    jQuery.noConflict();
            
            jQuery.ajax({
                url:"/search?phrase="+value, //�޸����url���������� 
                dataType:'json',  
                data:'',  
                jsonp:'callback',   
                //async: false
                type:'GET',
               // dataType:'json',
                    success : function(result) {  
                        if(result){
                            tableNode=document.createElement("table");//��ö��� 
                            tableNode.setAttribute("id","table");
                            var div_index=0;//��¼������DIV������
                            //console.log(result)    
        
                            var dataObj=eval(result);  
                            
                            var table_index=0;
                            for(var x=0;x<3;x++){ 
                                var trNode=tableNode.insertRow(); 
                                for(var y=0;y<3;y++){
                                    var tdNode=trNode.insertCell(); 
                                    if(dataObj.length > table_index)
                                    {
                                        tdNode.innerHTML=dataObj[table_index].name+"<a href=\"javascript:test('"+dataObj[table_index].name+"')\">";//��һ�������� ���ǻ���֪������զд 
                                        table_index++; 
                                        //break;
                                    }        
                                } 
                            } 
                            document.getElementById("recommend").appendChild(tableNode);//��ӵ��Ǹ�λ�� 
                            
                        }
                    },
                    error : function(XMLHttpRequest, textStatus, errorThrown) { 
                        console.log(errorThrown)   
                    } 
            });
    
    
    
}
