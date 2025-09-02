import { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useMyOrganization, useCreateOrganization, useInviteUser } from '../hooks/useOrganizations';
import { useTodos, useCreateTodo, useUpdateTodo, useDeleteTodo } from '../hooks/useTodos';
import { useNotes, useCreateNote, useUpdateNote, useDeleteNote } from '../hooks/useNotes';
import Navigation from '../components/Navigation';

export default function Dashboard() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [showCreateOrg, setShowCreateOrg] = useState(false);
  const [showInviteUser, setShowInviteUser] = useState(false);
  const [showCreateTodo, setShowCreateTodo] = useState(false);
  const [showCreateNote, setShowCreateNote] = useState(false);
  const [orgName, setOrgName] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteUsername, setInviteUsername] = useState('');
  const [inviteRole, setInviteRole] = useState('MEMBER');
  const [todoTitle, setTodoTitle] = useState('');
  const [todoDescription, setTodoDescription] = useState('');
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');

  const { data: organization, isLoading: orgLoading, error: orgError } = useMyOrganization();
  const { data: todos, isLoading: todosLoading } = useTodos();
  const { data: notes, isLoading: notesLoading } = useNotes();
  const createOrgMutation = useCreateOrganization();
  const inviteUserMutation = useInviteUser();
  const createTodoMutation = useCreateTodo();
  const updateTodoMutation = useUpdateTodo();
  const deleteTodoMutation = useDeleteTodo();
  const createNoteMutation = useCreateNote();
  const updateNoteMutation = useUpdateNote();
  const deleteNoteMutation = useDeleteNote();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleCreateOrg = async (e) => {
    e.preventDefault();
    try {
      await createOrgMutation.mutateAsync({ name: orgName });
      setOrgName('');
      setShowCreateOrg(false);
    } catch (err) {
      alert('Failed to create organization');
    }
  };

  const handleInviteUser = async (e) => {
    e.preventDefault();
    try {
      const response = await inviteUserMutation.mutateAsync({
        email: inviteEmail,
        username: inviteUsername,
        role: inviteRole
      });
      setInviteEmail('');
      setInviteUsername('');
      setInviteRole('MEMBER');
      setShowInviteUser(false);
      
      // Show the temporary password to the admin
      if (response.data.temporary_password) {
        alert(`User invited successfully!\n\nTemporary Password: ${response.data.temporary_password}\n\nPlease share this password with the new user. They should change it after their first login.`);
      } else {
        alert('User invited successfully');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to invite user';
      alert(`Error: ${errorMessage}`);
      console.error('Invite error:', err.response?.data);
    }
  };

  const handleCreateTodo = async (e) => {
    e.preventDefault();
    try {
      await createTodoMutation.mutateAsync({
        title: todoTitle,
        description: todoDescription
      });
      setTodoTitle('');
      setTodoDescription('');
      setShowCreateTodo(false);
    } catch (err) {
      alert('Failed to create todo');
    }
  };

  const handleToggleTodo = async (todo) => {
    try {
      console.log('Toggling todo:', todo.id, 'completed:', !todo.completed);
      await updateTodoMutation.mutateAsync({
        todoId: todo.id,
        data: { 
          completed: !todo.completed 
        }
      });
    } catch (err) {
      console.error('Toggle todo error:', err.response?.data);
      alert(`Failed to update todo: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleDeleteTodo = async (todoId) => {
    if (window.confirm('Are you sure you want to delete this todo?')) {
      try {
        await deleteTodoMutation.mutateAsync(todoId);
      } catch (err) {
        alert('Failed to delete todo');
      }
    }
  };

  const handleCreateNote = async (e) => {
    e.preventDefault();
    try {
      await createNoteMutation.mutateAsync({
        title: noteTitle,
        content: noteContent
      });
      setNoteTitle('');
      setNoteContent('');
      setShowCreateNote(false);
    } catch (err) {
      alert('Failed to create note');
    }
  };

  const handleDeleteNote = async (noteId) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      try {
        await deleteNoteMutation.mutateAsync(noteId);
      } catch (err) {
        alert('Failed to delete note');
      }
    }
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  const renderOverview = () => (
    <div>
      <h2>Overview</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
        <div style={{ 
          padding: '1.5rem', 
          border: '1px solid #ddd', 
          borderRadius: '8px',
          backgroundColor: '#f8f9fa'
        }}>
          <h3>User Information</h3>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Role:</strong> {user.role}</p>
          <p><strong>User ID:</strong> {user.id}</p>
        </div>
        
        <div style={{ 
          padding: '1.5rem', 
          border: '1px solid #ddd', 
          borderRadius: '8px',
          backgroundColor: '#f8f9fa'
        }}>
          <h3>Quick Stats</h3>
          <p><strong>Organization:</strong> {organization ? organization.name : 'None'}</p>
          <p><strong>Total Todos:</strong> {todos ? todos.length : 0}</p>
          <p><strong>Completed Todos:</strong> {todos ? todos.filter(t => t.completed).length : 0}</p>
          <p><strong>Total Notes:</strong> {notes ? notes.length : 0}</p>
        </div>
      </div>
    </div>
  );

  const renderTodos = () => (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Todos</h2>
        {organization && (
          <button 
            onClick={() => setShowCreateTodo(true)}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Add Todo
          </button>
        )}
      </div>

      {!organization ? (
        <p>You need to be part of an organization to manage todos.</p>
      ) : (
        <>
          {showCreateTodo && (
            <form onSubmit={handleCreateTodo} style={{ 
              border: '1px solid #ddd', 
              padding: '1rem', 
              borderRadius: '4px',
              marginBottom: '1rem',
              backgroundColor: '#f8f9fa'
            }}>
              <h4>Create New Todo</h4>
              <div style={{ marginBottom: '0.5rem' }}>
                <input
                  type="text"
                  placeholder="Todo Title"
                  value={todoTitle}
                  onChange={(e) => setTodoTitle(e.target.value)}
                  required
                  style={{ width: '100%', padding: '0.5rem' }}
                />
              </div>
              <div style={{ marginBottom: '0.5rem' }}>
                <textarea
                  placeholder="Description (optional)"
                  value={todoDescription}
                  onChange={(e) => setTodoDescription(e.target.value)}
                  style={{ width: '100%', padding: '0.5rem', minHeight: '80px' }}
                />
              </div>
              <button type="submit" style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                marginRight: '0.5rem'
              }}>
                Create
              </button>
              <button 
                type="button" 
                onClick={() => setShowCreateTodo(false)}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </form>
          )}

          {todosLoading ? (
            <p>Loading todos...</p>
          ) : todos && todos.length > 0 ? (
            <div>
              {todos.map(todo => (
                <div key={todo.id} style={{ 
                  padding: '1rem', 
                  border: '1px solid #ddd', 
                  borderRadius: '4px',
                  marginBottom: '0.5rem',
                  backgroundColor: todo.completed ? '#f8f9fa' : 'white'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <h4 style={{ 
                        margin: '0 0 0.5rem 0', 
                        textDecoration: todo.completed ? 'line-through' : 'none',
                        color: todo.completed ? '#6c757d' : 'inherit'
                      }}>
                        {todo.title}
                      </h4>
                      {todo.description && (
                        <p style={{ 
                          margin: '0 0 0.5rem 0',
                          color: todo.completed ? '#6c757d' : 'inherit'
                        }}>
                          {todo.description}
                        </p>
                      )}
                      <small style={{ color: '#6c757d' }}>
                        Created: {new Date(todo.created_at).toLocaleDateString()}
                        {todo.updated_at && todo.updated_at !== todo.created_at && (
                          <span> | Updated: {new Date(todo.updated_at).toLocaleDateString()}</span>
                        )}
                      </small>
                    </div>
                    <div style={{ marginLeft: '1rem' }}>
                      <button
                        onClick={() => handleToggleTodo(todo)}
                        style={{
                          padding: '0.25rem 0.5rem',
                          backgroundColor: todo.completed ? '#ffc107' : '#28a745',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          marginRight: '0.5rem'
                        }}
                      >
                        {todo.completed ? 'Undo' : 'Complete'}
                      </button>
                      {user.role === 'ADMIN' && (
                        <button
                          onClick={() => handleDeleteTodo(todo.id)}
                          style={{
                            padding: '0.25rem 0.5rem',
                            backgroundColor: '#dc3545',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                          }}
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No todos yet. Create your first todo!</p>
          )}
        </>
      )}
    </div>
  );

  const renderOrganization = () => (
    <div>
      <h2>Organization</h2>
      {orgLoading ? (
        <p>Loading organization...</p>
      ) : orgError ? (
        <div>
          <p>You're not part of any organization yet.</p>
          {!showCreateOrg ? (
            <button 
              onClick={() => setShowCreateOrg(true)}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Create Organization
            </button>
          ) : (
            <form onSubmit={handleCreateOrg} style={{ 
              marginTop: '1rem',
              padding: '1rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              backgroundColor: '#f8f9fa'
            }}>
              <h4>Create New Organization</h4>
              <input
                type="text"
                placeholder="Organization Name"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                required
                style={{ padding: '0.5rem', marginRight: '0.5rem', width: '200px' }}
              />
              <button type="submit" style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                marginRight: '0.5rem'
              }}>
                Create
              </button>
              <button 
                type="button" 
                onClick={() => setShowCreateOrg(false)}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </form>
          )}
        </div>
      ) : (
        <div>
          <div style={{ 
            padding: '1rem', 
            border: '1px solid #ddd', 
            borderRadius: '8px',
            backgroundColor: '#f8f9fa',
            marginBottom: '2rem'
          }}>
            <h3>{organization.name}</h3>
            <p><strong>Created:</strong> {new Date(organization.created_at).toLocaleDateString()}</p>
            <p><strong>Total Members:</strong> {organization.members?.length || 0}</p>
          </div>
          
          {/* Members List */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h4>Members</h4>
              {user.role === 'ADMIN' && (
                <button 
                  onClick={() => setShowInviteUser(true)}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Invite User
                </button>
              )}
            </div>

            {organization.members?.map(member => (
              <div key={member.id} style={{ 
                padding: '0.75rem', 
                border: '1px solid #ddd', 
                borderRadius: '4px',
                marginBottom: '0.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <strong>{member.username}</strong> 
                  <span style={{ 
                    marginLeft: '0.5rem',
                    padding: '0.2rem 0.5rem',
                    backgroundColor: member.role === 'ADMIN' ? '#dc3545' : '#007bff',
                    color: 'white',
                    borderRadius: '12px',
                    fontSize: '0.8rem'
                  }}>
                    {member.role}
                  </span>
                  {member.email && <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>{member.email}</div>}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#6c757d' }}>
                  Joined: {new Date(member.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}

            {showInviteUser && user.role === 'ADMIN' && (
              <form onSubmit={handleInviteUser} style={{ 
                border: '1px solid #ddd', 
                padding: '1rem', 
                borderRadius: '4px',
                backgroundColor: '#f8f9fa',
                marginTop: '1rem'
              }}>
                <h5>Invite New User</h5>
                <p style={{ fontSize: '0.9rem', color: '#6c757d', marginBottom: '1rem' }}>
                  This will create a new user account and add them to your organization with a temporary password.
                </p>
                <div style={{ marginBottom: '0.5rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                    Email Address *
                  </label>
                  <input
                    type="email"
                    placeholder="user@example.com"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    required
                    style={{ width: '100%', padding: '0.5rem' }}
                  />
                </div>
                <div style={{ marginBottom: '0.5rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                    Username *
                  </label>
                  <input
                    type="text"
                    placeholder="username (3-50 characters)"
                    value={inviteUsername}
                    onChange={(e) => setInviteUsername(e.target.value)}
                    required
                    minLength={3}
                    maxLength={50}
                    style={{ width: '100%', padding: '0.5rem' }}
                  />
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.25rem', fontWeight: 'bold' }}>
                    Role
                  </label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem' }}
                  >
                    <option value="MEMBER">Member - Can view and manage todos/notes</option>
                    <option value="ADMIN">Admin - Full organization management</option>
                  </select>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button 
                    type="submit" 
                    disabled={inviteUserMutation.isPending}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      flex: 1
                    }}
                  >
                    {inviteUserMutation.isPending ? 'Inviting...' : 'Send Invite'}
                  </button>
                  <button 
                    type="button" 
                    onClick={() => {
                      setShowInviteUser(false);
                      setInviteEmail('');
                      setInviteUsername('');
                      setInviteRole('MEMBER');
                    }}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#6c757d',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const renderNotes = () => (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Notes</h2>
        {organization && (
          <button 
            onClick={() => setShowCreateNote(true)}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Add Note
          </button>
        )}
      </div>

      {!organization ? (
        <p>You need to be part of an organization to manage notes.</p>
      ) : (
        <>
          {showCreateNote && (
            <form onSubmit={handleCreateNote} style={{ 
              border: '1px solid #ddd', 
              padding: '1rem', 
              borderRadius: '4px',
              marginBottom: '1rem',
              backgroundColor: '#f8f9fa'
            }}>
              <h4>Create New Note</h4>
              <div style={{ marginBottom: '0.5rem' }}>
                <input
                  type="text"
                  placeholder="Note Title"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  required
                  style={{ width: '100%', padding: '0.5rem' }}
                />
              </div>
              <div style={{ marginBottom: '0.5rem' }}>
                <textarea
                  placeholder="Note Content"
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  required
                  style={{ width: '100%', padding: '0.5rem', minHeight: '120px' }}
                />
              </div>
              <button type="submit" style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                marginRight: '0.5rem'
              }}>
                Create
              </button>
              <button 
                type="button" 
                onClick={() => setShowCreateNote(false)}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </form>
          )}

          {notesLoading ? (
            <p>Loading notes...</p>
          ) : notes && notes.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
              {notes.map(note => (
                <div key={note.id} style={{ 
                  padding: '1rem', 
                  border: '1px solid #ddd', 
                  borderRadius: '8px',
                  backgroundColor: 'white',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <h4 style={{ margin: '0', flex: 1 }}>{note.title}</h4>
                    {user.role === 'ADMIN' && (
                      <button
                        onClick={() => handleDeleteNote(note.id)}
                        style={{
                          padding: '0.25rem 0.5rem',
                          backgroundColor: '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '0.8rem'
                        }}
                      >
                        Delete
                      </button>
                    )}
                  </div>
                  <div style={{ 
                    marginBottom: '0.5rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}>
                    {note.content}
                  </div>
                  <small style={{ color: '#6c757d' }}>
                    Created: {new Date(note.created_at).toLocaleDateString()}
                    {note.updated_at && note.updated_at !== note.created_at && (
                      <span> | Updated: {new Date(note.updated_at).toLocaleDateString()}</span>
                    )}
                  </small>
                </div>
              ))}
            </div>
          ) : (
            <p>No notes yet. Create your first note!</p>
          )}
        </>
      )}
    </div>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'todos':
        return renderTodos();
      case 'notes':
        return renderNotes();
      case 'organization':
        return renderOrganization();
      default:
        return renderOverview();
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '2rem',
        borderBottom: '1px solid #ccc',
        paddingBottom: '1rem'
      }}>
        <h1>Dashboard</h1>
        <div>
          <span style={{ marginRight: '1rem' }}>Welcome, {user.username}!</span>
          <button 
            onClick={handleLogout}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </header>
      
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      
      {renderContent()}
    </div>
  );
}
