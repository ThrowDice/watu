var skin = {};
skin['BORDER_COLOR'] = '#cccccc';
skin['ENDCAP_BG_COLOR'] = '#F3F3F3';
skin['ENDCAP_TEXT_COLOR'] = '#333333';
skin['ENDCAP_LINK_COLOR'] = '#0000cc';
skin['ALTERNATE_BG_COLOR'] = '#F3F3F3';
skin['CONTENT_BG_COLOR'] = '#F3F3F3';
skin['CONTENT_LINK_COLOR'] = '#0000cc';
skin['CONTENT_TEXT_COLOR'] = '#333333';
skin['CONTENT_SECONDARY_LINK_COLOR'] = '#7777cc';
skin['CONTENT_SECONDARY_TEXT_COLOR'] = '#666666';
skin['CONTENT_HEADLINE_COLOR'] = '#333333';
skin['DEFAULT_COMMENT_TEXT'] = '- add your comment here -';
skin['HEADER_TEXT'] = 'Comments';
skin['POSTS_PER_PAGE'] = '5';
google.friendconnect.container.setParentUrl('/' /* location of rpc_relay.html and canvas.html */);
google.friendconnect.container.renderWallGadget(
 { id: 'googleFriendComment',
   site: '13734485586428459180',
   'view-params':{"scope":"SITE","features":"video,comment"}
},
  skin);

var skin = {};
skin['HEIGHT'] = '385';
skin['BORDER_COLOR'] = '#cccccc';
skin['ENDCAP_BG_COLOR'] = '#F3F3F3';
skin['ENDCAP_TEXT_COLOR'] = '#333333';
skin['ENDCAP_LINK_COLOR'] = '#0000cc';
skin['ALTERNATE_BG_COLOR'] = '#F3F3F3';
skin['CONTENT_BG_COLOR'] = '#F3F3F3';
skin['CONTENT_LINK_COLOR'] = '#0000cc';
skin['CONTENT_TEXT_COLOR'] = '#333333';
skin['CONTENT_SECONDARY_LINK_COLOR'] = '#7777cc';
skin['CONTENT_SECONDARY_TEXT_COLOR'] = '#666666';
skin['CONTENT_HEADLINE_COLOR'] = '#333333';
google.friendconnect.container.setParentUrl('/' /* location of rpc_relay.html and canvas.html */);
google.friendconnect.container.renderMembersGadget(
 { id: 'googleFriendConnect',
   site: '13734485586428459180'},
  skin);

var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));

try {
var pageTracker = _gat._getTracker("UA-6708285-1");
pageTracker._trackPageview();
} catch(err) {}

$(document).ready(function(){
	if($.cookie('message')!=1)
		$("#message").show('fast');

	$("#message a").click(function(e){
		$("#message").hide('slow');
		$.cookie('message','1',{'expires':100,'path':'/'});
		return false;
	});

//	if(($mainPicture=$('#mainPicture')) && $mainPicture.height()<300)
//		$mainPicture.addClass('small');
});
