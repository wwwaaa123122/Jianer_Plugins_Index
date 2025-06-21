<?php
error_reporting(0);

require 'login.class.php';
$login=new qq_login();
if($_GET['do']=='checkvc'){
	$array=$login->checkvc($_POST['uin']);
}
elseif($_GET['do']=='dovc'){
	$array=$login->dovc($_POST['uin'],$_POST['sig'],$_POST['ans'],$_POST['cap_cd'],$_POST['sess'],$_POST['websig'],$_POST['cdata'],$_POST['sid']);
}
elseif($_GET['do']=='getvc'){
	$array=$login->getvc($_POST['uin'],$_POST['sig'],$_POST['sess'],$_POST['sid'],$_POST['websig']);
}
elseif($_GET['do']=='qqlogin'){
	$array=$login->qqlogin($_POST['uin'],$_POST['pwd'],$_POST['p'],$_POST['vcode'],$_POST['pt_verifysession'],$_POST['sid'],$_POST['cookie'],$_POST['sms_code'],$_POST['sms_ticket']);
}
elseif($_GET['do']=='smscode'){
	$array=$login->send_sms_code($_POST['uin'],$_POST['sms_ticket'],$_POST['cookie']);
}
elseif($_GET['do']=='getqrpic'){
	$array=$login->getqrpic();
}
elseif($_GET['do']=='qrlogin'){
	if(isset($_GET['findpwd']))session_start();
	$array=$login->qrlogin($_GET['qrsig']);
}
elseif($_GET['do']=='getqrpic3rd'){
	$array=$login->getqrpic3rd($_GET['daid'],$_GET['appid']);
}
elseif($_GET['do']=='qrlogin3rd'){
	$array=$login->qrlogin3rd($_GET['daid'],$_GET['appid'],$_GET['qrsig']);
}
elseif($_GET['do']=='apigetqrpic'){
    session_start();
    $uin = isset($_REQUEST['uin']) ? trim($_REQUEST['uin']) : '';
    if(empty($uin) || !is_numeric($uin)){
        $array = array('saveOK'=>-1,'msg'=>'uin不能为空');
    }else{
        $token = md5($uin . uniqid() . mt_rand(1000,9999));
        $qrinfo = $login->getqrpic();
        if(isset($qrinfo['saveOK']) && $qrinfo['saveOK'] == 0){
            $_SESSION['apilogin'][$token] = array(
                'uin' => $uin,
                'qrsig' => $qrinfo['qrsig'],
                'qrcode' => $qrinfo['qrcode'],
                'data' => $qrinfo['data'],
                'status' => 0,
                'keys' => null,
                'time' => time()
            );
            $sid = session_id(); // 新增
            $host = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] == 'on' ? 'https://' : 'http://') . $_SERVER['HTTP_HOST'];
            $base = $host . dirname($_SERVER['REQUEST_URI']);
            $qrcode_url = $base . '/login.php?do=apigetqrimg&token=' . $token . '&sid=' . $sid; // 新增sid
            $web_login_url = $base . '/index2.html?token=' . $token . '&sid=' . $sid; // 新增sid
            $array = array('saveOK'=>0,'msg'=>'二维码获取成功','token'=>$token,'qrcode'=>'data:image/png;base64,'.$qrinfo['data'],'qrcode_url'=>$qrcode_url,'web_login_url'=>$web_login_url, 'sid'=>$sid); // 新增sid
        }else{
            $array = array('saveOK'=>-2,'msg'=>'二维码获取失败');
        }
    }
}
elseif($_GET['do']=='apigetqrimg'){
    if(isset($_REQUEST['sid']) && $_REQUEST['sid']){
        session_id($_REQUEST['sid']);
    }
    session_start();
    $token = isset($_REQUEST['token']) ? trim($_REQUEST['token']) : '';
    if(empty($token) || !isset($_SESSION['apilogin'][$token])){
        header('Content-Type: application/json');
        echo json_encode(array('saveOK'=>-1,'msg'=>'token无效'));
        exit;
    }
    $info = $_SESSION['apilogin'][$token];
    $imgdata = base64_decode($info['data']);
    header('Content-Type: image/png');
    echo $imgdata;
    exit;
}
elseif($_GET['do']=='apigetresult'){
    if(isset($_REQUEST['sid']) && $_REQUEST['sid']){
        session_id($_REQUEST['sid']);
    }
    session_start();
    $token = isset($_REQUEST['token']) ? trim($_REQUEST['token']) : '';
    if(empty($token) || !isset($_SESSION['apilogin'][$token])){
        $array = array('saveOK'=>-1,'msg'=>'token无效');
    }else{
        $info = &$_SESSION['apilogin'][$token];
        // 检查是否已登录
        if($info['status'] == 2 && $info['keys']){
            $array = array('saveOK'=>0,'msg'=>'登录成功','uin'=>$info['uin'],'keys'=>$info['keys']);
        }else{
            // 轮询二维码状态
            $qrres = $login->qrlogin($info['qrsig']);
            if(isset($qrres['saveOK']) && $qrres['saveOK'] == 0){
                // 登录成功，保存key
                $info['status'] = 2;
                $info['keys'] = array(
                    'uin' => $qrres['uin'],
                    'nick' => $qrres['nick'],
                    'skey' => $qrres['skey'],
                    'pskey' => $qrres['pskey'],
                    'superkey' => $qrres['superkey']
                );
                $array = array('saveOK'=>0,'msg'=>'登录成功','uin'=>$qrres['uin'],'keys'=>$info['keys']);
            }elseif(isset($qrres['saveOK']) && $qrres['saveOK'] == 3){
                $info['status'] = 1;
                $array = array('saveOK'=>3,'msg'=>'已扫码，等待确认');
            }elseif(isset($qrres['saveOK']) && $qrres['saveOK'] == 2){
                $array = array('saveOK'=>2,'msg'=>'请使用QQ手机版扫描二维码');
            }elseif(isset($qrres['saveOK']) && $qrres['saveOK'] == 1){
                $array = array('saveOK'=>1,'msg'=>'二维码已失效');
            }else{
                $array = array('saveOK'=>-2,'msg'=>'未知错误');
            }
        }
    }
}
header('Content-type: application/json');
echo json_encode($array);
