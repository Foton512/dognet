(function () {
    'use strict';

    angular
        .module('app.services')
        .factory('VkLoginService', ['$q', '$timeout', VkLoginService]);

	function VkLoginService($q, $timeout) {
        var url_parser={
            get_args: function (s) {
                var tmp=new Array();
                s=(s.toString()).split('&');
                for (var i in s) {
                    i=s[i].split("=");
                    tmp[(i[0])]=i[1];
                }
                return tmp;
            },
            get_args_cookie: function (s) {
                var tmp=new Array();
                s=(s.toString()).split('; ');
                for (var i in s) {
                    i=s[i].split("=");
                    tmp[(i[0])]=i[1];
                }
                return tmp;
            }
        };

        var plugin_vk = {
            wwwref: false,
            plugin_perms: "friends,wall,photos,messages,wall,offline,notes",

            auth: function () {
                var defer = $q.defer();
                if (!window.localStorage.getItem("plugin_vk_token") || window.localStorage.getItem("plugin_vk_perms")!=plugin_vk.plugin_perms) {
                    var authURL = "https://oauth.vk.com/authorize?client_id=5115660&display=mobile&redirect_uri=https://oauth.vk.com/blank.html&response_type=token&v=5.37&scope=offline";
                    window.authwindow = window.open(authURL, '_blank', 'location=no');
                    window.authwindow.addEventListener('loadstop', function (event) {
                        var tmp=(event.url).split("#");
                        if (tmp[0]=='https://oauth.vk.com/blank.html') {
                            var tmp=url_parser.get_args(tmp[1]);
                            window.authwindow.close();
                            window.localStorage.setItem("plugin_vk_token", tmp['access_token']);
                            window.localStorage.setItem("plugin_vk_user_id", tmp['user_id']);
                            window.localStorage.setItem("plugin_vk_exp", tmp['expires_in']);
                            window.localStorage.setItem("plugin_vk_perms", plugin_vk.plugin_perms);
                        }
                        $timeout(function() {
                            if(window.localStorage.getItem("plugin_vk_token")){
                                defer.resolve();
                            }
                        }, 0);
                    });
                }else{
                    defer.reject();
                }
                return defer.promise;
            }
        };
        return plugin_vk;
	}

})();