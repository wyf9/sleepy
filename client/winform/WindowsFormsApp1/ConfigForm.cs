using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Windows.Forms;

namespace SleepyWinform
{
    public partial class ConfigForm : Form
    {
        private const string ConfigFileName = "config.ini";
        public Config Resconfigs = new Config();

        public ConfigForm()
        {
            InitializeComponent();
        }

        private void config_Load(object sender, EventArgs e)
        {
            initConfig();
        }

        public void initConfig()
        {
            string filePath = Path.Combine(Application.StartupPath, ConfigFileName);
            Resconfigs = LoadConfig(filePath);

            // 绑定配置到界面
            server_textbox.Text = Resconfigs.Host;
            serverport_box.Text = Resconfigs.Port.ToString();
            device_textbox.Text = Resconfigs.device;
            secret_textBox.Text = Resconfigs.secret;
            blacklists_box.Text = string.Join(",", Resconfigs.blacklists);
        }

        public static Config LoadConfig(string filePath)
        {
            var config = new Config();

            if (!File.Exists(filePath))
            {
                MessageBox.Show("配置文件不存在，已创建示例配置，请修改后重新加载", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                Config.SaveConfig("https://expmale.com", 443, "winform-pc", "114514", "任务切换,开始菜单",false);
                return config;
            }

            try
            {
                var lines = File.ReadAllLines(filePath);
                foreach (var line in lines)
                {
                    var trimmedLine = line.Trim();
                    if (string.IsNullOrEmpty(trimmedLine) || trimmedLine.StartsWith("#") || trimmedLine.StartsWith(";"))
                        continue;

                    var parts = trimmedLine.Split(new[] { '=' }, 2);
                    if (parts.Length != 2) continue;

                    var key = parts[0];
                    var value = parts[1];

                    switch (key)
                    {
                        case "Host":
                            config.Host = value;
                            break;
                        case "Port":
                            config.Port = int.Parse(value);
                            break;
                        case "device":
                            config.device = value;
                            break;
                        case "deviceid":
                            config.deviceid = value;
                            break;
                        case "secret":
                            config.secret = value;
                            break;
                        case "blacklists":
                            config.blacklists = value.Split(',')
                                .Select(s => s.Trim())
                                .Where(s => !string.IsNullOrEmpty(s))
                                .ToList();
                            break;
                        case "logfile":
                            config.logfile=bool.Parse(value);
                            break;
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"加载配置失败：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return config;
            }

            // 校验
            if (string.IsNullOrEmpty(config.Host) || config.Port <= 1 || config.Port >= 25565 || string.IsNullOrEmpty(config.device))
            {
                string message = "当前配置项无效，\n\n" +
                    $"Host: {config.Host}\n" +
                    $"Port: {config.Port}\n" +
                    $"Device: {config.device}\n" +
                    $"Secret: {config.secret}\n" +
                    $"blacklists: {config.blacklists}\n" +
                    $"日志: {config.logfile}\n" +
                    "已将错误配置重置为示例配置";

                MessageBox.Show(message, "警告", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                Config.SaveConfig("https://expmale.com", 443, "winform-pc", "114514", "任务切换,开始菜单",false);
                return config;
            }

            return config;
        }

        // 保存配置
        //public static void SaveConfig(string filePath, string host, int port, string device, string secret, string blacklists)
        //{
        //    var configLines = new List<string>
        //    {
        //        "# 自动生成的配置文件",
        //        $"Host={host}",
        //        $"Port={port}",
        //        $"device={device}",
        //        $"deviceid={Guid.NewGuid().ToString()}",
        //        $"secret={secret}"
        //    };

        //    if (!string.IsNullOrWhiteSpace(blacklists))
        //    {
        //        configLines.Add($"blacklists={blacklists}");
        //    }

        //    try
        //    {
        //        File.WriteAllLines(filePath, configLines);
        //        MessageBox.Show("配置保存成功", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
        //    }
        //    catch (Exception ex)
        //    {
        //        MessageBox.Show($"保存配置失败：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
        //    }
        //}

        private void button1_Click(object sender, EventArgs e)
        {
            initConfig();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            //string filePath = Path.Combine(Application.StartupPath, ConfigFileName);
            Config.SaveConfig(server_textbox.Text, int.Parse(serverport_box.Text), device_textbox.Text, secret_textBox.Text, blacklists_box.Text,logY.Checked);
            this.DialogResult = DialogResult.OK;
        }

        private void button3_Click(object sender, EventArgs e)
        {
            if (secret_textBox.PasswordChar == '\0')
            {
                secret_textBox.PasswordChar = '*';
                button3.Text = "👁️";
            }
            else
            {
                secret_textBox.PasswordChar = '\0';
                button3.Text = "🙈";
            }
        }
    }
}
