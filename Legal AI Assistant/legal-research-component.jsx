import React, { useState, useEffect } from 'react';

const GenesisAIResearchPlatform = () => {
  const [activeTab, setActiveTab] = useState('research');
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI Legal Research Assistant. Ask me anything about case law, legislation, or legal concepts. I can help with research, document analysis, and finding relevant precedents.'
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [documentAnalysis, setDocumentAnalysis] = useState(null);
  const [citationNetwork, setCitationNetwork] = useState(null);

  // Simulated AI search function
  const performAISearch = async (query) => {
    setLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const mockResults = [
      {
        id: 1,
        type: 'case',
        title: 'Smith v. Jones Holdings Ltd [2024] HCA 45',
        court: 'High Court of Australia',
        year: 2024,
        categories: ['Contract Law', 'Employment Law'],
        snippet: 'The High Court held that a material breach of an employment contract occurs when an employer fails to provide agreed-upon benefits...',
        relevance: 0.95
      },
      {
        id: 2,
        type: 'legislation',
        title: 'Fair Work Act 2009 (Cth) s 386',
        jurisdiction: 'Commonwealth',
        categories: ['Employment Law'],
        snippet: 'Section 386 defines dismissal for the purposes of unfair dismissal claims, including constructive dismissal...',
        relevance: 0.88
      },
      {
        id: 3,
        type: 'article',
        title: 'Johnson & Partners (2023) - Breach of Contract in Employment',
        publication: 'Employment Law Review',
        year: 2023,
        categories: ['Employment Law', 'Contract Law'],
        snippet: 'This comprehensive analysis explores the elements of breach of contract in employment relationships...',
        relevance: 0.82
      }
    ];
    
    setResults(mockResults);
    setLoading(false);
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      performAISearch(searchQuery);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');

    // Simulate AI response
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const aiResponse = {
      role: 'assistant',
      content: `Based on your question about "${chatInput}", I found relevant case law and legislation. The key principle established in Smith v. Jones [2024] HCA 45 is that material breach occurs when agreed benefits are unilaterally reduced. This is supported by Fair Work Act s 386 which defines constructive dismissal. Would you like me to elaborate on any specific aspect?`
    };
    
    setChatMessages(prev => [...prev, aiResponse]);
  };

  const analyzeMockDocument = () => {
    setDocumentAnalysis({
      issues: [
        { severity: 'high', title: 'Indemnification Gap', location: 'Section 4.3, Page 7' },
        { severity: 'medium', title: 'Unclear Termination Clause', location: 'Section 2.1, Page 3' },
        { severity: 'medium', title: 'Missing Force Majeure', location: 'N/A' }
      ],
      risks: {
        high: ['Indemnification provisions may not adequately protect client'],
        medium: ['Termination notice period conflicts with industry standard'],
        low: ['Payment terms are within acceptable range']
      },
      suggestions: [
        'Add comprehensive force majeure clause',
        'Clarify exclusive jurisdiction provisions',
        'Strengthen indemnification to include indirect damages'
      ]
    });
  };

  const loadCitationNetwork = () => {
    setCitationNetwork({
      primary: 'Smith v. Jones [2024] HCA 45',
      related: [
        { name: 'Brown v. Corp Ltd [2023]', connection: 'Employment Contract Breach', strength: 0.9 },
        { name: 'Wilson v. Enterprises [2023]', connection: 'Constructive Dismissal', strength: 0.85 },
        { name: 'Taylor v. Industries [2022]', connection: 'Material Breach', strength: 0.8 },
        { name: 'Anderson v. Group [2021]', connection: 'Remedies', strength: 0.75 }
      ]
    });
  };

  useEffect(() => {
    if (activeTab === 'citations' && !citationNetwork) {
      loadCitationNetwork();
    }
  }, [activeTab]);

  const TabButton = ({ id, label, badge }) => (
    <button
      onClick={() => setActiveTab(id)}
      style={{
        padding: '1rem 2rem',
        background: activeTab === id ? 'linear-gradient(135deg, #e84a27 0%, #ff6b47 100%)' : 'white',
        color: activeTab === id ? 'white' : '#6c757d',
        border: 'none',
        borderRadius: '8px 8px 0 0',
        fontSize: '1rem',
        fontWeight: '600',
        cursor: 'pointer',
        transition: 'all 0.3s',
        marginRight: '0.5rem',
        boxShadow: activeTab === id ? '0 -2px 10px rgba(232, 74, 39, 0.2)' : 'none'
      }}
    >
      {label}
      {badge && (
        <span style={{
          marginLeft: '0.5rem',
          padding: '0.25rem 0.5rem',
          background: activeTab === id ? 'rgba(255,255,255,0.3)' : '#28a745',
          borderRadius: '10px',
          fontSize: '0.7rem',
          fontWeight: '700'
        }}>
          {badge}
        </span>
      )}
    </button>
  );

  const SearchResult = ({ result }) => (
    <div style={{
      padding: '1.5rem',
      background: '#f8f9fa',
      borderLeft: '4px solid #e84a27',
      borderRadius: '8px',
      marginBottom: '1rem',
      transition: 'all 0.3s'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.background = 'white';
      e.currentTarget.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.background = '#f8f9fa';
      e.currentTarget.style.boxShadow = 'none';
    }}>
      <div style={{ 
        fontWeight: '700', 
        color: '#1a3a52', 
        fontSize: '1.1rem', 
        marginBottom: '0.5rem' 
      }}>
        {result.title}
      </div>
      <div style={{
        display: 'flex',
        gap: '1rem',
        fontSize: '0.875rem',
        color: '#6c757d',
        marginBottom: '0.5rem'
      }}>
        <span>📅 {result.year}</span>
        <span>⚖️ {result.court || result.jurisdiction || result.publication}</span>
        <span>🔖 {result.categories.join(', ')}</span>
        <span style={{ color: '#28a745' }}>✓ {Math.round(result.relevance * 100)}% relevant</span>
      </div>
      <div style={{ color: '#2c3e50', lineHeight: '1.6' }}>
        {result.snippet}
      </div>
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
        <button style={actionButtonStyle}>View Full Text</button>
        <button style={secondaryButtonStyle}>Add to Outline</button>
        <button style={secondaryButtonStyle}>Export Citation</button>
      </div>
    </div>
  );

  const actionButtonStyle = {
    padding: '0.5rem 1rem',
    background: '#1a3a52',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '0.875rem',
    cursor: 'pointer',
    transition: 'all 0.3s'
  };

  const secondaryButtonStyle = {
    padding: '0.5rem 1rem',
    background: '#f8f9fa',
    color: '#1a3a52',
    border: '1px solid #dee2e6',
    borderRadius: '6px',
    fontSize: '0.875rem',
    cursor: 'pointer',
    transition: 'all 0.3s'
  };

  return (
    <div style={{ 
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      background: '#f8f9fa',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #1a3a52 0%, #0f2538 100%)',
        color: 'white',
        padding: '1rem 2rem',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        position: 'sticky',
        top: 0,
        zIndex: 1000
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ fontSize: '1.8rem', fontWeight: '700' }}>
            Lex<span style={{ color: '#e84a27' }}>AI</span> Research
          </div>
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
            <span>Dashboard</span>
            <span>Research</span>
            <span>Documents</span>
            <span>Analytics</span>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              background: 'rgba(255,255,255,0.1)',
              borderRadius: '20px'
            }}>
              <span>👤</span>
              <span>Jane Smith, Esq.</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem' }}>
        {/* Hero Section */}
        <div style={{
          background: 'linear-gradient(135deg, white 0%, #e8f4f8 100%)',
          borderRadius: '16px',
          padding: '3rem',
          marginBottom: '2rem',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
        }}>
          <h1 style={{ 
            fontSize: '2.5rem', 
            color: '#1a3a52', 
            marginBottom: '1rem',
            fontWeight: '700'
          }}>
            AI-Powered Legal Research Platform
          </h1>
          <p style={{ fontSize: '1.2rem', color: '#6c757d', marginBottom: '2rem' }}>
            Accelerate your research with cutting-edge AI technology and comprehensive legal databases
          </p>

          {/* Stats */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem'
          }}>
            {[
              { number: '2.3M+', label: 'Legal Documents' },
              { number: '450K+', label: 'Case Citations' },
              { number: '98%', label: 'Accuracy Rate' },
              { number: '75%', label: 'Time Saved' }
            ].map((stat, i) => (
              <div key={i} style={{
                background: 'white',
                padding: '1.5rem',
                borderRadius: '12px',
                textAlign: 'center',
                boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
              }}>
                <div style={{ 
                  fontSize: '2.5rem', 
                  fontWeight: '700', 
                  color: '#e84a27',
                  marginBottom: '0.5rem'
                }}>
                  {stat.number}
                </div>
                <div style={{ color: '#6c757d', fontSize: '0.875rem' }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Search Box */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '2rem',
          boxShadow: '0 2px 15px rgba(0,0,0,0.1)',
          marginBottom: '2rem'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            fontSize: '1.1rem',
            fontWeight: '600',
            color: '#1a3a52',
            marginBottom: '1rem'
          }}>
            <span>Ask legal questions in everyday language</span>
            <span style={{
              background: 'linear-gradient(135deg, #e84a27 0%, #ff6b47 100%)',
              color: 'white',
              padding: '0.25rem 0.75rem',
              borderRadius: '20px',
              fontSize: '0.75rem',
              fontWeight: '700'
            }}>
              AI POWERED
            </span>
          </div>
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="e.g., What are the elements of breach of contract in employment law?"
              style={{
                flex: 1,
                padding: '1rem 1.5rem',
                border: '2px solid #dee2e6',
                borderRadius: '8px',
                fontSize: '1rem',
                outline: 'none'
              }}
            />
            <button
              onClick={handleSearch}
              style={{
                padding: '1rem 2.5rem',
                background: 'linear-gradient(135deg, #e84a27 0%, #ff6b47 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s'
              }}
            >
              🔍 Search
            </button>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {[
              'Statute of Limitations',
              'Employment Discrimination',
              'Environmental Law',
              'IP Infringement'
            ].map(suggestion => (
              <div
                key={suggestion}
                onClick={() => setSearchQuery(`What are recent cases on ${suggestion}?`)}
                style={{
                  padding: '0.5rem 1rem',
                  background: '#f8f9fa',
                  border: '1px solid #dee2e6',
                  borderRadius: '20px',
                  fontSize: '0.875rem',
                  cursor: 'pointer',
                  transition: 'all 0.3s'
                }}
              >
                {suggestion}
              </div>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <div style={{ marginBottom: '2rem' }}>
          <TabButton id="research" label="AI Research" badge="NEW" />
          <TabButton id="documents" label="Document Review" badge="BETA" />
          <TabButton id="citations" label="Citations" />
          <TabButton id="outline" label="Outline" />
          <TabButton id="assistant" label="AI Assistant" />
        </div>

        {/* Tab Content */}
        <div style={{
          background: 'white',
          borderRadius: '0 12px 12px 12px',
          padding: '2rem',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          minHeight: '400px'
        }}>
          {activeTab === 'research' && (
            <div>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '3rem' }}>
                  <div style={{
                    border: '4px solid #dee2e6',
                    borderTop: '4px solid #e84a27',
                    borderRadius: '50%',
                    width: '50px',
                    height: '50px',
                    animation: 'spin 1s linear infinite',
                    margin: '0 auto 1rem'
                  }} />
                  <p>Searching comprehensive legal database...</p>
                </div>
              ) : results.length > 0 ? (
                <div>
                  <h2 style={{ marginBottom: '1.5rem', color: '#1a3a52' }}>
                    Research Results
                  </h2>
                  {results.map(result => (
                    <SearchResult key={result.id} result={result} />
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#6c757d' }}>
                  <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
                  <p>Enter a search query to find relevant cases, legislation, and legal commentary</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'documents' && (
            <div>
              <div
                onClick={analyzeMockDocument}
                style={{
                  border: '3px dashed #dee2e6',
                  borderRadius: '12px',
                  padding: '3rem',
                  textAlign: 'center',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  marginBottom: '2rem'
                }}
              >
                <div style={{ fontSize: '3rem', color: '#e84a27', marginBottom: '1rem' }}>📤</div>
                <h3>Upload Documents for AI Review</h3>
                <p style={{ color: '#6c757d', marginTop: '0.5rem' }}>
                  Drag and drop files here or click to browse<br />
                  Supported: PDF, DOCX, TXT (Max 50MB)
                </p>
              </div>

              {documentAnalysis && (
                <div>
                  <h3 style={{ marginBottom: '1rem' }}>Document Analysis</h3>
                  
                  <div style={{ marginBottom: '1rem', padding: '1.5rem', background: '#f8f9fa', borderLeft: '4px solid #e84a27', borderRadius: '8px' }}>
                    <div style={{ fontWeight: '700', marginBottom: '0.5rem' }}>🔍 Key Issues Identified</div>
                    <ul style={{ marginLeft: '1.5rem', marginTop: '0.5rem' }}>
                      {documentAnalysis.issues.map((issue, i) => (
                        <li key={i}>{issue.title} ({issue.location})</li>
                      ))}
                    </ul>
                  </div>

                  <div style={{ marginBottom: '1rem', padding: '1.5rem', background: '#f8f9fa', borderLeft: '4px solid #e84a27', borderRadius: '8px' }}>
                    <div style={{ fontWeight: '700', marginBottom: '0.5rem' }}>⚠️ Risk Assessment</div>
                    <div style={{ marginTop: '0.5rem' }}>
                      {documentAnalysis.risks.high.map((risk, i) => (
                        <div key={i}><strong style={{ color: '#e84a27' }}>High Risk:</strong> {risk}</div>
                      ))}
                      {documentAnalysis.risks.medium.map((risk, i) => (
                        <div key={i}><strong style={{ color: '#ffc107' }}>Medium Risk:</strong> {risk}</div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'citations' && citationNetwork && (
            <div>
              <h3 style={{ marginBottom: '1.5rem' }}>Citation Network Analysis</h3>
              <p style={{ marginBottom: '1rem', color: '#6c757d' }}>
                Discover conceptually related cases that don't directly cite each other
              </p>
              
              <div style={{ textAlign: 'center', margin: '2rem 0' }}>
                <div style={{
                  display: 'inline-block',
                  padding: '1rem 1.5rem',
                  background: '#1a3a52',
                  color: 'white',
                  borderRadius: '20px',
                  fontSize: '1rem'
                }}>
                  {citationNetwork.primary}
                </div>
              </div>

              {citationNetwork.related.map((related, i) => (
                <div key={i} style={{ textAlign: 'center', margin: '1rem 0' }}>
                  <div style={{ color: '#6c757d', marginBottom: '0.5rem' }}>
                    ↓ Related by: {related.connection} ({Math.round(related.strength * 100)}%) ↓
                  </div>
                  <div style={{
                    display: 'inline-block',
                    padding: '0.5rem 1rem',
                    background: '#e84a27',
                    color: 'white',
                    borderRadius: '20px',
                    margin: '0.5rem',
                    cursor: 'pointer'
                  }}>
                    {related.name}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'outline' && (
            <div>
              <h3 style={{ marginBottom: '1.5rem' }}>Research Outline</h3>
              {['Introduction', 'Elements of Breach', 'Remedies', 'Conclusion'].map((section, i) => (
                <div key={i} style={{
                  padding: '1rem',
                  background: '#f8f9fa',
                  borderLeft: '3px solid #e84a27',
                  marginBottom: '0.5rem',
                  borderRadius: '6px',
                  cursor: 'move'
                }}>
                  <strong>{['I', 'II', 'III', 'IV'][i]}. {section}</strong>
                </div>
              ))}
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.5rem' }}>
                <button style={actionButtonStyle}>+ Add Section</button>
                <button style={secondaryButtonStyle}>Export to Word</button>
              </div>
            </div>
          )}

          {activeTab === 'assistant' && (
            <div style={{ display: 'flex', flexDirection: 'column', height: '500px' }}>
              <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem', padding: '1rem' }}>
                {chatMessages.map((msg, i) => (
                  <div key={i} style={{
                    padding: '1rem',
                    marginBottom: '1rem',
                    borderRadius: '8px',
                    maxWidth: '80%',
                    background: msg.role === 'user' ? '#1a3a52' : '#f8f9fa',
                    color: msg.role === 'user' ? 'white' : '#2c3e50',
                    marginLeft: msg.role === 'user' ? 'auto' : '0'
                  }}>
                    {msg.content}
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                  placeholder="Ask a follow-up question..."
                  style={{
                    flex: 1,
                    padding: '1rem',
                    border: '2px solid #dee2e6',
                    borderRadius: '8px',
                    fontSize: '1rem',
                    outline: 'none'
                  }}
                />
                <button onClick={sendChatMessage} style={{
                  padding: '1rem 2rem',
                  background: 'linear-gradient(135deg, #e84a27 0%, #ff6b47 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}>
                  Send
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default GenesisAIResearchPlatform;
