SKIPMOUNT=true
PROPFILE=false
POSTFSDATA=false
LATESTARTSERVICE=true
CONFIG_PATH=/data/adb/modules/zmal-sleepy/config.cfg

set_perm_recursive $MODPATH 0 0 0777 0777

if [ -f $CONFIG_PATH ]; then
    echo "配置文件存在，跳过复制"
else
    echo "配置文件不存在，复制"
    cp $MODPATH/config.cfg $CONFIG_PATH
fi
echo "配置文件在${CONFIG_PATH}"
echo ""
echo "推荐先修改后重启手机"
