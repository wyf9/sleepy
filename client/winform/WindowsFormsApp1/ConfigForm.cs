using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;

namespace WindowsFormsApp1
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

        private void initConfig()
        {
            string filePath = Path.Combine(Application.StartupPath, ConfigFileName);
            Resconfigs = LoadConfig(filePath);

            // 绑定配置到界面
            textBox1.Text = Resconfigs.Server;
            textBox2.Text = Resconfigs.ServerPort;
            textBox3.Text = Resconfigs.device;
            textBox4.Text = Resconfigs.secret;
        }

        private Config LoadConfig(string filePath)
        {
            var config = new Config();

            if (!File.Exists(filePath))
            {
                CreateSampleConfig(filePath);
                MessageBox.Show("配置文件不存在，已创建示例配置，请修改后重新加载", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return config; // 返回空配置，需用户修改后保存
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
                        case "Server": config.Server = value; break;
                        case "ServerPort": config.ServerPort = value; break;
                        case "device": config.device = value; break;
                        case "secret": config.secret = value; break;
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"加载配置失败：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return new Config(); // 返回默认配置
            }

            // 验证必填项
            if (string.IsNullOrEmpty(config.Server) || string.IsNullOrEmpty(config.ServerPort) || string.IsNullOrEmpty(config.device))
            {
                MessageBox.Show("配置项缺失（Server、ServerPort、device为必填项），已重置为示例配置", "警告", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                CreateSampleConfig(filePath);
                return LoadConfig(filePath); // 重新加载新生成的示例配置
            }

            return config;
        }

        private void CreateSampleConfig(string filePath)
        {
            var sampleLines = new List<string>
            {
                "# 示例配置文件",
                "# Server地址",
                "Server=example.com",
                "# 服务器端口",
                "ServerPort=443",
                "# 设备名称",
                "device=YourDeviceName",
                "# 密钥",
                "secret=123456"
            };
            File.WriteAllLines(filePath, sampleLines);
        }

        private void SaveConfig()
        {
            string filePath = Path.Combine(Application.StartupPath, ConfigFileName);
            var configLines = new List<string>
            {
                "# 自动生成的配置文件",
                $"Server={textBox1.Text.Trim()}",
                $"ServerPort={textBox2.Text.Trim()}",
                $"device={textBox3.Text.Trim()}",
                $"secret={textBox4.Text.Trim()}"
            };

            try
            {
                File.WriteAllLines(filePath, configLines);
                MessageBox.Show("配置保存成功", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"保存配置失败：{ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            initConfig();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            SaveConfig();
            this.DialogResult = DialogResult.OK;
        }
    }

   
}