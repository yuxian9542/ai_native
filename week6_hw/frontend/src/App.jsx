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
  ExclamationCircleOutlined,
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
    
    // 调试日志
    console.log(`收到服务器消息: ${data.type}`, data);
    
    // 如果是最终结果或错误，取消处理状态
    if (data.type === 'analysis_complete' || 
        data.type === 'error' || 
        data.type === 'code_generation_error' ||
        data.type === 'execution_error' ||
        data.type === 'execution_exception' ||
        data.type === 'execution_success') {
      console.log('重置处理状态为 false');
      setIsProcessing(false);
    }
  };

  const sendMessage = () => {
    if (!inputValue.trim()) return;
    if (!isConnected) {
      message.error('未连接到服务器');
      return;
    }

    // 如果正在处理，显示中断提示
    if (isProcessing) {
      message.info('正在中断当前任务，开始处理新问题...');
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
    
    // 添加超时保护，确保处理状态能够重置
    setTimeout(() => {
      if (isProcessing) {
        console.warn('处理超时，自动重置处理状态');
        setIsProcessing(false);
        message.warning('处理超时，请重试');
      }
    }, 60000); // 60秒超时
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

      case 'data_analysis':
        return (
          <Card 
            key={index} 
            className="message-card"
            title={<><BarChartOutlined /> 数据分析</>}
            size="small"
          >
            <div style={{ marginBottom: 12 }}>
              <Text strong>需要的数据：</Text>
              <div style={{ marginTop: 8, padding: 8, background: '#f0f5ff', borderRadius: 4 }}>
                <div><Text type="secondary">表格：</Text> {msg.content.required_data.tables?.join(', ') || '未知'}</div>
                <div><Text type="secondary">列：</Text> {msg.content.required_data.columns?.join(', ') || '未知'}</div>
                <div><Text type="secondary">数据类型：</Text> {msg.content.required_data.data_types?.join(', ') || '未知'}</div>
              </div>
            </div>

            <div style={{ marginBottom: 12 }}>
              <Text strong>需要的函数：</Text>
              <div style={{ marginTop: 8 }}>
                {msg.content.required_functions?.map((func, i) => (
                  <Tag key={i} color="blue" style={{ marginRight: 4, marginBottom: 4 }}>
                    {func}
                  </Tag>
                ))}
              </div>
            </div>

            {msg.content.data_values && Object.keys(msg.content.data_values).length > 0 && (
              <div style={{ marginBottom: 12 }}>
                <Text strong>具体数据数值：</Text>
                <div style={{ marginTop: 8, padding: 8, background: '#f6ffed', borderRadius: 4 }}>
                  {Object.entries(msg.content.data_values).map(([column, values]) => (
                    <div key={column} style={{ marginBottom: 4 }}>
                      <Text type="secondary">{column}：</Text>
                      <Text code style={{ fontSize: '12px' }}>
                        {Array.isArray(values) ? values.slice(0, 5).join(', ') + (values.length > 5 ? '...' : '') : String(values)}
                      </Text>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {msg.content.analysis_explanation && (
              <div>
                <Text strong>分析解释：</Text>
                <div style={{ 
                  marginTop: 8, 
                  padding: 8, 
                  background: '#fff7e6', 
                  borderRadius: 4,
                  border: '1px solid #ffd591'
                }}>
                  <Text>{msg.content.analysis_explanation}</Text>
                </div>
              </div>
            )}
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

      case 'execution_success':
        return (
          <Card 
            key={index} 
            className="message-card"
            title={<><CheckCircleOutlined /> 代码执行成功</>}
            size="small"
          >
            <Tag color="green">执行成功</Tag>
            <Tag color="blue">第{msg.content.attempt}次尝试</Tag>
            <Tag color="orange">耗时: {msg.content.execution_time?.toFixed(2)}秒</Tag>
            {msg.content.image_generated && <Tag color="purple">已生成图表</Tag>}
            <div style={{ marginTop: 8 }}>
              <Text type="success">✅ 代码执行完成，正在生成分析结果...</Text>
            </div>
          </Card>
        );

      case 'execution_error':
        return (
          <Card 
            key={index} 
            className="message-card"
            title={<><ExclamationCircleOutlined /> 代码执行失败</>}
            size="small"
          >
            <Tag color="red">执行失败</Tag>
            <Tag color="blue">第{msg.content.attempt}次尝试</Tag>
            <Tag color="orange">耗时: {msg.content.execution_time?.toFixed(2)}秒</Tag>
            <Tag color="purple">代码长度: {msg.content.code_length}字符</Tag>
            <div style={{ marginTop: 12 }}>
              <Text type="danger">❌ 执行错误详情：</Text>
              <div style={{ 
                marginTop: 8, 
                padding: 12, 
                background: '#fff2f0', 
                borderRadius: 4,
                border: '1px solid #ffccc7',
                fontFamily: 'monospace',
                fontSize: '12px',
                whiteSpace: 'pre-wrap',
                maxHeight: '300px',
                overflow: 'auto'
              }}>
                {msg.content.error}
              </div>
            </div>
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
                <Text type="secondary">工作表：</Text> {msg.content.full_data_trace?.sheet_name || '未知'}
                <br />
                <Text type="secondary">使用列：</Text> {msg.content.used_columns.join(', ')}
                <br />
                <Text type="secondary">文件描述：</Text> {msg.content.file_summary}
              </div>
              
              {/* 完整数据溯源 */}
              {msg.content.full_data_trace && msg.content.full_data_trace.column_data && (
                <div style={{ marginTop: 12 }}>
                  <Text strong>所用列的完整数值：</Text>
                  {Object.entries(msg.content.full_data_trace.column_data).map(([column, data]) => (
                    <div key={column} style={{ marginTop: 8, padding: 8, background: '#fff', borderRadius: 4, border: '1px solid #d9d9d9' }}>
                      <Text strong style={{ color: '#1890ff' }}>{column}</Text>
                      <div style={{ marginTop: 4 }}>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          共 {data.total_unique_count} 个唯一值
                        </Text>
                      </div>
                      <div style={{ marginTop: 4, maxHeight: '100px', overflowY: 'auto' }}>
                        <Text code style={{ fontSize: '11px', lineHeight: '1.4' }}>
                          {data.unique_values.slice(0, 20).join(', ')}
                          {data.unique_values.length > 20 && '...'}
                        </Text>
                      </div>
                    </div>
                  ))}
                </div>
              )}
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

