import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export default function Navigation({ activeTab, onTabChange }) {
  const { user } = useContext(AuthContext);

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'todos', label: 'Todos' },
    { id: 'notes', label: 'Notes' },
    { id: 'organization', label: 'Organization' },
  ];

  return (
    <nav style={{ 
      borderBottom: '1px solid #ccc', 
      marginBottom: '2rem',
      paddingBottom: '1rem'
    }}>
      <div style={{ display: 'flex', gap: '1rem' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: activeTab === tab.id ? '#007bff' : 'transparent',
              color: activeTab === tab.id ? 'white' : '#007bff',
              border: '1px solid #007bff',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </nav>
  );
}
