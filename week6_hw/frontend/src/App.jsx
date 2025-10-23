import React, { useState, useEffect, useRef } from 'react';
import { Layout, Input, Button, Card, Typography, Tag, Spin, Badge, message, Upload, Progress, List, Space, Tooltip, Divider } from 'antd';
import {
  SendOutlined,
  AudioOutlined,
  UserOutlined,
  RobotOutlined,
  FolderOutlined,
  CodeOutlined,
  BarChartOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  UploadOutlined,
  FileExcelOutlined,
  DeleteOutlined,
  PlusOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './App.css';

const { Header, Content, Footer, Sider } = Layout;
const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [deletingFiles, setDeletingFiles] = useState(new Set());
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // WebSocket连接
  useEffect(() => {
    connectWebSocket();
    fetchFileList(); // 获取已上传的文件列表
    
    // 初始化语音识别
    if ('webkitSpeechRecognition' in window) {
      const recognition = new webkitSpeechRecognition();
      recognition.lang = 'zh-CN';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        setIsListening(false);
      };

      recognition.onerror = (event) => {
        console.error('语音识别错误:', event.error);
        message.error('语音识别失败');
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  // 自动滚动
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/chat');

    ws.onopen = () => {
      console.log('WebSocket连接成功');
      setIsConnected(true);
      message.success('连接成功');
    };

    ws.onclose = () => {
      console.log('WebSocket连接关闭');
      setIsConnected(false);
      message.warning('连接已断开');
      // 尝试重连
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
      setIsConnected(false);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleServerMessage(data);
    };

    wsRef.current = ws;
  };

  const handleServerMessage = (data) => {
    setMessages(prev => [...prev, { type: data.type, content: data.content, from: 'server' }]);
    
    // 如果是最终结果或错误，取消处理状态
    if (data.type === 'analysis_complete' || data.type === 'error') {
      setIsProcessing(false);
    }
  };

  const sendMessage = () => {
    if (!inputValue.trim()) return;
    if (!isConnected) {
      message.error('未连接到服务器');
      return;
    }

    // 添加用户消息
    setMessages(prev => [...prev, { type: 'user', content: inputValue, from: 'user' }]);

    // 发送到服务器
    wsRef.current.send(JSON.stringify({
      type: 'text',
      content: inputValue
    }));

    setInputValue('');
    setIsProcessing(true);
  };

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      message.error('您的浏览器不支持语音识别');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
      message.info('请开始说话...');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 文件上传处理
  const handleFileUpload = async (file) => {
    setIsUploading(true);
    setUploadProgress(0);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);
      
      const response = await fetch('http://localhost:8000/api/files/upload', {
        method: 'POST',
        body: formData,
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      const result = await response.json();
      
      if (result.success) {
        message.success(`文件 ${file.name} 上传成功！`);
        setUploadedFiles(prev => [...prev, {
          file_id: result.file_id,
          file_name: result.file_name,
          upload_time: new Date().toLocaleString()
        }]);
        
        // 添加成功消息到聊天
        setMessages(prev => [...prev, {
          type: 'upload_success',
          content: {
            file_name: result.file_name,
            file_id: result.file_id
          },
          from: 'system'
        }]);
      } else {
        message.error(`上传失败: ${result.error}`);
      }
    } catch (error) {
      message.error(`上传失败: ${error.message}`);
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
    
    return false; // 阻止默认上传行为
  };

  // 获取文件列表
  const fetchFileList = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/files');
      const result = await response.json();
      if (result.files) {
        setUploadedFiles(result.files.map(file => ({
          file_id: file.file_id,
          file_name: file.file_name,
          upload_time: new Date(file.created_at).toLocaleString()
        })));
      }
    } catch (error) {
      console.error('获取文件列表失败:', error);
    }
  };

  // 删除文件
  const deleteFile = async (fileId, fileName) => {
    try {
      // 设置删除状态
      setDeletingFiles(prev => new Set(prev).add(fileId));
      
      const response = await fetch(`http://localhost:8000/api/files/${fileId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const result = await response.json();
        message.success(result.message || '文件删除成功');
        // 从UI中移除文件
        setUploadedFiles(prevFiles => prevFiles.filter(file => file.file_id !== fileId));
      } else {
        const error = await response.json();
        message.error(error.detail || '删除失败');
        // 如果删除失败，重新获取文件列表以恢复UI状态
        fetchFileList();
      }
    } catch (error) {
      console.error('删除文件失败:', error);
      message.error('删除文件失败');
      // 如果删除失败，重新获取文件列表以恢复UI状态
      fetchFileList();
    } finally {
      // 清除删除状态
      setDeletingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(fileId);
        return newSet;
      });
    }
  };

  const renderMessage = (msg, index) => {
    switch (msg.type) {
      case 'user':
        return (
          <Card 
            key={index} 
            className="message-card user-message"
            size="small"
          >
            <div className="message-content">
              <UserOutlined style={{ marginRight: 8, color: '#1890ff' }} />
              <Text strong>你：</Text>
              <Paragraph style={{ marginLeft: 8, marginBottom: 0 }}>{msg.content}</Paragraph>
            </div>
          </Card>
        );

      case 'status':
        return (
          <Card key={index} className="message-card status-message" size="small">
            <Spin size="small" style={{ marginRight: 8 }} />
            <Text type="secondary">{msg.content}</Text>
          </Card>
        );

      case 'files_found':
        return (
          <Card 
            key={index} 
            className="message-card"
            title={<><FolderOutlined /> 找到相关文件</>}
            size="small"
          >
            {msg.content.files.map((file, i) => (
              <Card.Grid key={i} style={{ width: '100%', padding: '12px' }}>
                <Text strong>{file.name}</Text>
                <br />
                <Text type="secondary">{file.summary}</Text>
                <br />
                <Tag color="blue">匹配度: {file.score}</Tag>
              </Card.Grid>
            ))}
          </Card>
        );

      case 'code_generated':
        return (
          <Card 
            key={index} 
            className="message-card"
            title={<><CodeOutlined /> 生成的分析代码</>}
            size="small"
          >
            <Tag color="green">{msg.content.analysis_type}</Tag>
            <Tag color="blue">使用列: {msg.content.used_columns.join(', ')}</Tag>
            <SyntaxHighlighter 
              language="python" 
              style={vscDarkPlus}
              customStyle={{ marginTop: 12, borderRadius: 4 }}
            >
              {msg.content.code}
            </SyntaxHighlighter>
          </Card>
        );

      case 'analysis_complete':
        return (
          <Card 
            key={index} 
            className="message-card"
            title={<><BarChartOutlined /> 分析结果</>}
            size="small"
          >
            <Tag icon={<CheckCircleOutlined />} color="success">分析完成</Tag>
            
            {/* 文字输出 */}
            {msg.content.output && (
              <div style={{ marginTop: 12 }}>
                <Text strong>分析结果：</Text>
                <pre style={{ 
                  background: '#f5f5f5', 
                  padding: 12, 
                  borderRadius: 4,
                  whiteSpace: 'pre-wrap',
                  marginTop: 8
                }}>
                  {msg.content.output}
                </pre>
              </div>
            )}

            {/* 图片输出 */}
            {msg.content.image && (
              <div style={{ marginTop: 12 }}>
                <Text strong>可视化图表：</Text>
                <img 
                  src={`data:image/png;base64,${msg.content.image}`} 
                  alt="分析图表"
                  style={{ maxWidth: '100%', marginTop: 8, borderRadius: 4 }}
                />
              </div>
            )}

            {/* 数据溯源 */}
            <div style={{ marginTop: 12, padding: 12, background: '#f0f5ff', borderRadius: 4 }}>
              <Text strong>数据溯源：</Text>
              <div style={{ marginTop: 8 }}>
                <Text type="secondary">使用文件：</Text> {msg.content.used_file}
                <br />
                <Text type="secondary">使用列：</Text> {msg.content.used_columns.join(', ')}
                <br />
                <Text type="secondary">文件描述：</Text> {msg.content.file_summary}
              </div>
            </div>
          </Card>
        );

      case 'error':
        return (
          <Card 
            key={index} 
            className="message-card error-message"
            size="small"
          >
            <CloseCircleOutlined style={{ marginRight: 8, color: '#ff4d4f' }} />
            <Text type="danger">{msg.content}</Text>
          </Card>
        );

      case 'upload_success':
        return (
          <Card 
            key={index} 
            className="message-card"
            title={<><FileExcelOutlined /> 文件上传成功</>}
            size="small"
          >
            <Tag color="green" icon={<CheckCircleOutlined />}>已处理完成</Tag>
            <div style={{ marginTop: 8 }}>
              <Text strong>文件名：</Text> {msg.content.file_name}
              <br />
              <Text type="secondary">文件ID：</Text> {msg.content.file_id}
              <br />
              <Text type="secondary">状态：</Text> 已清洗并索引到Elasticsearch
            </div>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <Button
            type="text"
            icon={<FolderOutlined />}
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            style={{ color: 'white', fontSize: '16px' }}
            title={sidebarCollapsed ? '展开文件管理' : '折叠文件管理'}
          />
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            📊 Excel智能分析系统
          </Title>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <Badge 
            status={isConnected ? 'success' : 'error'} 
            text={<Text style={{ color: 'white' }}>{isConnected ? '已连接' : '未连接'}</Text>}
          />
          <Text style={{ color: 'white', fontSize: '12px' }}>
            已上传: {uploadedFiles.length} 个文件
          </Text>
        </div>
      </Header>

      <Layout>
        {/* 左侧文件管理面板 */}
        <Sider 
          width={300} 
          collapsed={sidebarCollapsed}
          collapsedWidth={60}
          className="file-sidebar"
          theme="light"
        >
          <div className="sidebar-header">
            {!sidebarCollapsed && (
              <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
                <Title level={5} style={{ margin: 0, display: 'flex', alignItems: 'center' }}>
                  <FolderOutlined style={{ marginRight: 8 }} />
                  文件管理
                </Title>
              </div>
            )}
            
            <div style={{ padding: '16px' }}>
              <Upload
                accept=".xlsx,.xls"
                beforeUpload={handleFileUpload}
                showUploadList={false}
                disabled={isUploading}
              >
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  loading={isUploading}
                  block={!sidebarCollapsed}
                  style={{ 
                    background: '#52c41a', 
                    borderColor: '#52c41a',
                    height: sidebarCollapsed ? '40px' : 'auto'
                  }}
                >
                  {sidebarCollapsed ? '' : (isUploading ? '上传中...' : '上传Excel')}
                </Button>
              </Upload>
              
              {isUploading && !sidebarCollapsed && (
                <Progress 
                  percent={uploadProgress} 
                  size="small" 
                  style={{ marginTop: 8 }}
                  status={uploadProgress === 100 ? 'success' : 'active'}
                />
              )}
            </div>
          </div>

          <div className="file-list-container">
            {!sidebarCollapsed ? (
              <List
                dataSource={uploadedFiles}
                locale={{ emptyText: '暂无文件' }}
                renderItem={(file) => (
                  <List.Item
                    key={file.file_id}
                    style={{
                      padding: '8px 16px',
                      opacity: deletingFiles.has(file.file_id) ? 0.5 : 1,
                      transition: 'opacity 0.3s ease'
                    }}
                    actions={[
                      <Tooltip title="删除文件">
                        <Button
                          type="text"
                          danger
                          size="small"
                          icon={<DeleteOutlined />}
                          loading={deletingFiles.has(file.file_id)}
                          onClick={() => deleteFile(file.file_id)}
                        />
                      </Tooltip>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={<FileExcelOutlined style={{ color: '#52c41a', fontSize: 16 }} />}
                      title={
                        <Text 
                          ellipsis={{ tooltip: file.file_name }}
                          style={{ fontSize: '12px' }}
                        >
                          {file.file_name}
                        </Text>
                      }
                      description={
                        <Space direction="vertical" size={2}>
                          <Text type="secondary" style={{ fontSize: '10px' }}>
                            {file.row_count} 行 × {file.column_count} 列
                          </Text>
                          <Text type="secondary" style={{ fontSize: '10px' }}>
                            {new Date(file.created_at).toLocaleDateString()}
                          </Text>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <div style={{ padding: '8px' }}>
                {uploadedFiles.map((file) => (
                  <Tooltip key={file.file_id} title={file.file_name}>
                    <Button
                      type="text"
                      icon={<FileExcelOutlined />}
                      style={{ 
                        width: '100%', 
                        height: '40px', 
                        marginBottom: '4px',
                        opacity: deletingFiles.has(file.file_id) ? 0.5 : 1
                      }}
                      onClick={() => deleteFile(file.file_id)}
                    />
                  </Tooltip>
                ))}
              </div>
            )}
          </div>
        </Sider>

        <Layout>
          <Content className="app-content">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <RobotOutlined style={{ fontSize: 48, color: '#1890ff' }} />
              <Title level={4}>欢迎使用Excel智能分析系统</Title>
              <Text type="secondary">
                请先在左侧上传Excel文件，然后输入您的问题进行分析
              </Text>
            </div>
          )}
          
          {messages.map((msg, index) => renderMessage(msg, index))}
          <div ref={messagesEndRef} />
        </div>
          </Content>

          <Footer className="app-footer">
        <div className="input-container">
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题（回车发送，Shift+回车换行）"
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={!isConnected || isProcessing}
          />
          <div className="button-group">
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={sendMessage}
              disabled={!isConnected || isProcessing || !inputValue.trim()}
            >
              发送
            </Button>
            <Button
              icon={<AudioOutlined />}
              onClick={toggleVoiceInput}
              disabled={!isConnected || isProcessing}
              danger={isListening}
              className={isListening ? 'voice-button-active' : ''}
            >
              {isListening ? '停止' : '语音'}
            </Button>
          </div>
        </div>
          </Footer>
        </Layout>
      </Layout>
    </Layout>
  );
}

export default App;

