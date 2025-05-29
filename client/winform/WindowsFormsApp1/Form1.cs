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

namespace WindowsFormsApp1
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }


        private void button1_Click(object sender, EventArgs e)
        {
            ConfigForm configForm = new ConfigForm();
            if (configForm.ShowDialog() == DialogResult.OK)
            {
                Config config = configForm.Resconfigs;
                //MessageBox.Show(config.secret);

            }
            else
            {
                MessageBox.Show("配置未完成");

            }
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            WindowWatcher.Start();
        }

        private void Form1_FormClosed(object sender, FormClosedEventArgs e)
        {
            WindowWatcher.Stop();
        }
    }
    public class Config
    {
        public string Server { get; set; }
        public string ServerPort { get; set; }
        public string device { get; set; }
        public string secret { get; set; }
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
            Console.WriteLine($"前台窗口变化: {windowTitle}");
        }
    }
}
