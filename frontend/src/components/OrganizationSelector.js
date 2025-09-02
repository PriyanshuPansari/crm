import { useState } from 'react';
import { useMyOrganizations } from '../hooks/useOrganizations';

const OrganizationSelector = ({ selectedOrgId, onOrganizationChange }) => {
  const { data: organizations, isLoading } = useMyOrganizations();
  const [isOpen, setIsOpen] = useState(false);

  if (isLoading) {
    return <div className="org-selector loading">Loading organizations...</div>;
  }

  if (!organizations || organizations.length === 0) {
    return <div className="org-selector">No organizations</div>;
  }

  const selectedOrg = organizations.find(org => org.id === selectedOrgId);

  return (
    <div className="org-selector">
      <div className="org-selector-button" onClick={() => setIsOpen(!isOpen)}>
        <span className="org-name">
          {selectedOrg ? selectedOrg.name : 'Select Organization'}
        </span>
        <span className="org-arrow">{isOpen ? '▲' : '▼'}</span>
      </div>
      
      {isOpen && (
        <div className="org-selector-dropdown">
          {organizations.map(org => (
            <div
              key={org.id}
              className={`org-option ${org.id === selectedOrgId ? 'selected' : ''}`}
              onClick={() => {
                onOrganizationChange(org.id);
                setIsOpen(false);
              }}
            >
              <div className="org-option-name">{org.name}</div>
              <div className="org-option-role">
                Role: {org.user_role || 'Member'}
              </div>
            </div>
          ))}
        </div>
      )}
      
      <style jsx>{`
        .org-selector {
          position: relative;
          margin-bottom: 20px;
        }
        
        .org-selector-button {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          user-select: none;
        }
        
        .org-selector-button:hover {
          border-color: #007bff;
        }
        
        .org-name {
          font-weight: 500;
        }
        
        .org-arrow {
          color: #666;
        }
        
        .org-selector-dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: white;
          border: 1px solid #ddd;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
          z-index: 1000;
          max-height: 300px;
          overflow-y: auto;
        }
        
        .org-option {
          padding: 12px 16px;
          border-bottom: 1px solid #eee;
          cursor: pointer;
        }
        
        .org-option:last-child {
          border-bottom: none;
        }
        
        .org-option:hover {
          background-color: #f8f9fa;
        }
        
        .org-option.selected {
          background-color: #e7f3ff;
          border-left: 3px solid #007bff;
        }
        
        .org-option-name {
          font-weight: 500;
          margin-bottom: 4px;
        }
        
        .org-option-role {
          font-size: 0.85em;
          color: #666;
        }
        
        .loading {
          padding: 12px 16px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: #f8f9fa;
          color: #666;
        }
      `}</style>
    </div>
  );
};

export default OrganizationSelector;
