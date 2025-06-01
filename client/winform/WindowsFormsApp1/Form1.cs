using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Net.Http;
using System.Text.Json;
using System.IO;
using System.Net.Sockets;

namespace SleepyWinform
{
    public partial class SleepyWinform : Form
    {
        public static Config config;
        public static SleepyWinform Instance;
        static string filePath = Path.Combine(Application.StartupPath, "config.ini");
        static string logFile = Path.Combine(Application.StartupPath, "log.txt");

        public SleepyWinform()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {

            WriteLog($"======{DateTime.Now.ToString("HH:mm:ss")}======");

            try
            {
                Instance = this;
                // 加载配置
                config = ConfigForm.LoadConfig(filePath);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"加载配置出错：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }

            WindowWatcher.Start();
        }

        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
            _ = SendPostRequestAsync(config, false, "");
            WindowWatcher.Stop();

        }

        // 配置按钮
        private void button1_Click(object sender, EventArgs e)
        {
            ConfigForm configForm = new ConfigForm();
            if (configForm.ShowDialog() == DialogResult.OK)
            {
                config = configForm.Resconfigs;
                // MessageBox.Show(config.secret); // 调试可打印
            }
            else
            {
                MessageBox.Show("配置未保存", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        public void AddResultToListView(string result)
        {
            // 内部检查线程安全性
            if (this.InvokeRequired)
            {
                this.Invoke((MethodInvoker)delegate
                {
                    AddResultToListView(result); // 递归调用直到在UI线程执行
                });
                return;
            }

            // 以下是UI线程安全的操作
            ListViewItem item = new ListViewItem(DateTime.Now.ToString("HH:mm:ss"));
            item.SubItems.Add(result);

            // 设置不同状态的颜色
            if (result.Contains("失败") || result.Contains("错误"))
                item.ForeColor = Color.Red;
            else if (result.Contains("成功"))
                item.ForeColor = Color.Green;

            listView1.Items.Add(item);
            listView1.EnsureVisible(listView1.Items.Count - 1);
        }

        //发送 POST 请求
        public static async Task SendPostRequestAsync(Config cfg, bool isUsing, string appName)
        {
            HttpClient httpClient = new HttpClient();

            Uri hostUri = new Uri(cfg.Host);
            UriBuilder uriBuilder = new UriBuilder
            {
                Scheme = hostUri.Scheme,
                Host = hostUri.Host,
                Port = (hostUri.Port == -1) ? cfg.Port : hostUri.Port,
                Path = "/device/set"
            };
            string url = uriBuilder.Uri.ToString();

            // 构造 JSON 数据
            var data = new
            {
                secret = cfg.secret,
                id = cfg.deviceid,
                show_name = cfg.device,
                @using = isUsing,
                app_name = appName
            };
            string json = JsonSerializer.Serialize(data);
            Console.WriteLine("POST URL: " + url);
            Console.WriteLine("POST Body: " + json);

            StringContent content = new StringContent(json, Encoding.UTF8, "application/json");

            try
            {
                //Console.WriteLine("尝试发送请求...");
                HttpResponseMessage response = await httpClient.PostAsync(url, content);

                string result = await response.Content.ReadAsStringAsync();
                //Console.WriteLine("请求结果: " + result);
                bool resultcode = JsonDocument.Parse(result).RootElement.GetProperty("success").GetBoolean();
                if (config != null&resultcode)
                {
                    WriteLog($"[{DateTime.Now.ToString("HH:mm:ss")}]-{appName}");
                    SleepyWinform.Instance.AddResultToListView(appName);

                }

            }
            catch (Exception ex)
            {
                Console.WriteLine("[请求失败] " + ex);
                WriteLog("[请求失败] " + ex);
                SleepyWinform.Instance.AddResultToListView($"[{appName}请求失败]-{ex}");
            }
        }

        public static void WriteLog(string message)
        {
            // 判断是否开启了日志记录
            if (config != null && config.logfile)
            {
                try
                {
                    File.AppendAllText(logFile, $"[{DateTime.Now.ToString("HH:mm:ss")}]{message}" + Environment.NewLine);
                }
                catch (Exception ex)
                {
                    Console.WriteLine("写入日志失败: " + ex.Message);
                }
            }
        }


    }

    public class Config
    {
        public string Host { get; set; }
        public int Port { get; set; }
        public string device { get; set; }
        public string deviceid { get; set; }
        public string secret { get; set; }
        public List<string> blacklists { get; set; } = new List<string>();
        public bool logfile { get; set; }

        // 文件保存路径
        public static string filePath { get; set; } = Path.Combine(Application.StartupPath, "config.ini");

        // 默认配置
        public Config()
        {
            Host = "https://asfag654-j.hf.space";
            Port = 443;
            device = "zmal-pc";
            deviceid = Guid.NewGuid().ToString();
            secret = "114514";
            blacklists = new List<string>() { };
            logfile = false;
        }

        public Config(string host, int port, string device, string secret)
        {
            this.Host = host;
            this.Port = port;
            this.device = device;
            this.secret = secret;
            this.deviceid = Guid.NewGuid().ToString();
            logfile = false;
        }

        public static void SaveConfig(string host, int port, string device, string secret, string blacklists,bool logfile)
        {
            List<string> configLines = new List<string>
                 {
                  "# 服务端地址",
                  $"Host={host}",
                  "# 服务端端口",
                  $"Port={port}",
                  "# 显示名称",
                  $"device={device}",
                  "# 设备id（随机生成",
                  $"deviceid={Guid.NewGuid().ToString()}",
                  "# 服务端密钥",
                  $"secret={secret}",
                  "# 黑名单列表",
                  $"blacklists={blacklists}",
                  "是否写入日志",
                  $"logfile={logfile}",
                 };


            try
            {
                File.WriteAllLines(filePath, configLines);
                MessageBox.Show("配置保存成功", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"保存配置失败：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

    }

    public class WindowWatcher
    {
        private delegate void WinEventDelegate(
            IntPtr hWinEventHook, uint eventType,
            IntPtr hwnd, int idObject, int idChild,
            uint dwEventThread, uint dwmsEventTime);

        private static WinEventDelegate procDelegate = new WinEventDelegate(WinEventProc);

        private const uint EVENT_SYSTEM_FOREGROUND = 0x0003;
        private const uint WINEVENT_OUTOFCONTEXT = 0;

        [DllImport("user32.dll")]
        private static extern IntPtr SetWinEventHook(
            uint eventMin, uint eventMax, IntPtr hmodWinEventProc,
            WinEventDelegate lpfnWinEventProc,
            uint idProcess, uint idThread, uint dwFlags);

        [DllImport("user32.dll")]
        private static extern bool UnhookWinEvent(IntPtr hWinEventHook);

        [DllImport("user32.dll")]
        private static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

        [DllImport("user32.dll")]
        private static extern int GetWindowTextLength(IntPtr hWnd);

        private static IntPtr _hook;

        public static void Start()
        {
            _hook = SetWinEventHook(EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND,
                IntPtr.Zero, procDelegate, 0, 0, WINEVENT_OUTOFCONTEXT);
        }

        public static void Stop()
        {
            if (_hook != IntPtr.Zero)
            {
                UnhookWinEvent(_hook);
            }
        }

        private static void WinEventProc(IntPtr hWinEventHook, uint eventType,
            IntPtr hwnd, int idObject, int idChild, uint dwEventThread, uint dwmsEventTime)
        {
            if (hwnd == IntPtr.Zero) return;

            int length = GetWindowTextLength(hwnd);
            StringBuilder builder = new StringBuilder(length + 1);
            GetWindowText(hwnd, builder, builder.Capacity);

            string windowTitle = builder.ToString();

            if (!string.IsNullOrEmpty(windowTitle))
            {
                Console.WriteLine($"前台窗口变化: {windowTitle}");

                // 黑名单判断（模糊匹配）
                if (SleepyWinform.config != null && SleepyWinform.config.blacklists != null)
                {
                    foreach (string blacklisted in SleepyWinform.config.blacklists)
                    {
                        if (!string.IsNullOrEmpty(blacklisted) && windowTitle.IndexOf(blacklisted, StringComparison.OrdinalIgnoreCase) >= 0)
                        {
                            // 如果标题中包含黑名单中的关键字，跳过
                            Console.WriteLine($"窗口 [{windowTitle}] 命中黑名单，跳过发送请求。");
                            //SleepyWinform.Instance?.AddResultToListView($"[{windowTitle}] 已在黑名单中，已跳过。");
                            return;
                        }
                    }
                }

                // 如果没有命中黑名单，发送请求
                _ = SleepyWinform.SendPostRequestAsync(SleepyWinform.config, true, windowTitle);
            }
            

        }
    }
}
