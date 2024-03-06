import re
import typing

from adbutils import AdbClient, WindowSize, RunningAppInfo
from adbutils._proto import AppInfo
from appium import webdriver
from appium.options.common import AppiumOptions


class Driver:
    def __init__(self, host: str, port: int, options: AppiumOptions):
        self._driver = webdriver.Remote(f"http://{host}:{port}", options=options)
        self._adb = AdbClient(host, port).device(options.get_capability("udid"))

    @property
    def bluetooth_on(self) -> bool:
        """
        是否启动蓝牙
        Returns:

        """
        status = int(self.shell("settings get global bluetooth_on"))
        return status == 1

    @property
    def wifi_on(self) -> bool:
        """
        是否启动Wi-Fi
        Returns:

        """
        status = "enabled" in self.shell('dumpsys wifi | grep "Wi-Fi is"')
        return status

    @property
    def airplane_mode_on(self) -> bool:
        """
        是否启动飞行模式
        Returns:

        """
        status = "enable" in self.shell("cmd connectivity airplane-mode")
        return status

    def is_ime_active(self) -> bool:
        """
        是否激活输入法
        Returns:

        """
        value = re.search(
            "mInputShown=(true|false)",
            self.shell("dumpsys input_method | grep mInputShown"),
        ).group(1)
        return value == "true"

    def is_screen_on(self) -> bool:
        """
        是否锁屏
        Returns:

        """
        return self._adb.is_screen_on()

    def get_brand(self) -> str:
        """
        获取设备品牌
        Returns:

        """
        brand = self.shell("getprop persist.sys.romtype") or self.shell(
            "getprop ro.product.manufacturer"
        )
        return brand

    def get_orientation(self) -> str:
        """
        屏幕方向
        0: 竖屏 1: 横屏
        Returns:

        """
        return self.shell("dumpsys input | grep SurfaceOrientation")

    def get_locale(self) -> str:
        """
        获取语言环境
        Returns:

        """
        locale = self.shell("getprop persist.sys.locale") or self.shell(
            "getprop ro.product.locale"
        )
        return locale

    def get_system_version(self) -> int:
        """
        获取系统版本
        Returns:

        """
        value = self.shell("getprop ro.build.version.release")
        return int(value)

    def get_build_number(self) -> str:
        """
        获取系统版本号
        Returns:

        """
        value = self.shell("getprop ro.fota.version")
        return value

    def get_device_model(self) -> str:
        """
        获取设备型号
        Returns:

        """
        return self.shell("getprop persist.sys.device") or self.shell(
            "getprop ro.product.model"
        )

    def get_packages(self) -> typing.List[str]:
        """
        获取包列表
        Returns:

        """
        return self._adb.list_packages()

    def get_current_ime(self) -> str:
        """
        获取当前输入法
        Returns:

        """
        return self.shell("settings get secure default_input_method")

    def get_window_size(self) -> WindowSize:
        """
        获取屏幕大小
        Returns:

        """
        if self._adb.rotation() == 0:
            return self._adb.__getattribute__("_raw_window_size")()
        return self._adb.window_size()

    def get_screen_timeout(self):
        """
        获取屏幕锁定时间
        Returns:

        """
        value = re.search(
            "mScreenOffTimeoutSetting=([0-9]+)",
            self.shell("dumpsys power | grep  mScreenOffTimeoutSetting"),
        ).group(1)
        return int(value)

    def get_max_volume_level(self) -> int:
        """
        获取最大音量等级
        Returns:

        """
        value = int(
            re.search(
                "Max: ([0-9]+)\n",
                self.shell('dumpsys audio | grep -A 5 "STREAM_MUSIC"'),
            ).group(1)
        )
        return value

    def get_max_notification_level(self) -> int:
        """
        获取最大提示音音量等级
        Returns:

        """
        value = int(
            re.search(
                "Max: ([0-9]+)\n",
                self.shell(
                    'dumpsys audio | grep -E "AUDIO_STREAM_RING|STREAM_NOTIFICATION" -A 5'
                ),
            ).group(1)
        )
        return value

    def get_volume_music_speaker(self):
        """
        获取音乐音量
        """
        value = int(
            re.search(
                "speaker=([0-9]+)",
                self.shell("settings list system | grep volume_music_speaker"),
            ).group(1)
        )
        return value

    def get_volume_notification_speaker(self):
        """
        获取铃声音量
        Returns:

        """
        return int(
            re.search(
                "speaker=([0-9]+)",
                self.shell("settings list system | grep volume_ring_speaker")
                or self.shell(
                    "settings list system | grep volume_notification_speaker"
                ),
            ).group(1)
        )

    def get_current_ssid(self) -> typing.Optional[str]:
        """
        获取当前连接的WiFi名称
        Returns:

        """
        if not (m := re.search(
                re.compile('(networkId|wifiNetworkKey)="(.+?)"'),
                self.shell('dumpsys netstats | grep -E "iface=wlan"'),
        )):
            return
        return m.group(2)

    def get_wlan_ip(self) -> str:
        """
        获取网络IP
        Returns:

        """
        return self._adb.wlan_ip()

    def get_bluetooth_name(self) -> str:
        """
        获取蓝牙名称
        Returns:

        """
        value = re.search(
            re.compile("name: (.+)\n"), self.shell("dumpsys bluetooth_manager")
        ).group(1)
        return value

    def get_screen_brightness(self) -> int:
        """
        获取屏幕亮度
        :return:
        """
        value = int(self.shell("settings get system screen_brightness"))
        return value

    def get_app_info(self, package_name: str) -> typing.Optional[AppInfo]:
        """
        获取应用信息
        Args:
            package_name:

        Returns:

        """
        return self._adb.app_info(package_name)

    def get_current_app(self) -> RunningAppInfo:
        """
        获取当前应用
        """
        return self._adb.app_current()

    def shell(self, cmdargs: typing.Union[str, list, tuple],
              timeout: typing.Optional[float] = None) -> str:
        """
        执行shell命令
        Args:
            cmdargs:
            timeout:

        Returns:

        """
        return self._adb.shell(cmdargs, timeout=timeout)
