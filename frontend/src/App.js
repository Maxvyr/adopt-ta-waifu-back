import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Components
const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <svg className="header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 19c-5 0-8-3-8-9s3-9 8-9 8 3 8 9-3 9-8 9z"/>
            <path d="M12 12l8-8"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          <h1>Idea Logger</h1>
        </div>
        <p className="header-subtitle">Capture, organize, and develop your ideas</p>
      </div>
    </header>
  );
};

const SearchBar = ({ searchTerm, setSearchTerm, onSearch }) => {
  return (
    <div className="search-container">
      <div className="search-input-wrapper">
        <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input
          type="text"
          placeholder="Search ideas..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && onSearch()}
          className="search-input"
        />
      </div>
    </div>
  );
};

const FilterTabs = ({ activeFilter, setActiveFilter, ideaCounts }) => {
  const tabs = [
    { key: 'all', label: 'All Ideas', count: ideaCounts.all },
    { key: 'active', label: 'Active', count: ideaCounts.active },
    { key: 'archived', label: 'Archived', count: ideaCounts.archived }
  ];

  return (
    <div className="filter-tabs">
      {tabs.map(tab => (
        <button
          key={tab.key}
          onClick={() => setActiveFilter(tab.key)}
          className={`filter-tab ${activeFilter === tab.key ? 'filter-tab-active' : 'filter-tab-inactive'}`}
        >
          {tab.label}
          <span className="filter-tab-count">{tab.count}</span>
        </button>
      ))}
    </div>
  );
};

const TagBadge = ({ tag, onClick, removable = false, onRemove }) => {
  return (
    <span className="tag-badge">
      <span onClick={onClick} className="tag-text">{tag}</span>
      {removable && (
        <button onClick={onRemove} className="tag-remove">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      )}
    </span>
  );
};

const IdeaCard = ({ idea, onEdit, onDelete, onArchive, onUnarchive }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="idea-card">
      <div className="idea-card-header">
        <h3 className="idea-title">{idea.title}</h3>
        <div className="idea-actions">
          <button onClick={() => onEdit(idea)} className="action-btn action-btn-edit">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
          {idea.status === 'active' ? (
            <button onClick={() => onArchive(idea.id)} className="action-btn action-btn-archive">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="21,8 21,21 3,21 3,8"/>
                <rect x="1" y="3" width="22" height="5"/>
                <line x1="10" y1="12" x2="14" y2="12"/>
              </svg>
            </button>
          ) : (
            <button onClick={() => onUnarchive(idea.id)} className="action-btn action-btn-unarchive">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="21,8 21,21 3,21 3,8"/>
                <rect x="1" y="3" width="22" height="5"/>
                <line x1="10" y1="12" x2="14" y2="12"/>
              </svg>
            </button>
          )}
          <button onClick={() => onDelete(idea.id)} className="action-btn action-btn-delete">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3,6 5,6 21,6"/>
              <path d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6m3,0V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2V6"/>
              <line x1="10" y1="11" x2="10" y2="17"/>
              <line x1="14" y1="11" x2="14" y2="17"/>
            </svg>
          </button>
        </div>
      </div>
      
      <div className="idea-content">
        <p>{idea.content}</p>
      </div>
      
      <div className="idea-meta">
        <div className="idea-category">
          <span className="category-badge">{idea.category}</span>
        </div>
        
        {idea.tags && idea.tags.length > 0 && (
          <div className="idea-tags">
            {idea.tags.map((tag, index) => (
              <TagBadge key={index} tag={tag} />
            ))}
          </div>
        )}
        
        <div className="idea-dates">
          <span className="date-text">
            {idea.status === 'archived' && '📦 '}
            Updated {formatDate(idea.updated_at)}
          </span>
        </div>
      </div>
    </div>
  );
};

const IdeaForm = ({ idea, onSave, onCancel, categories }) => {
  const [formData, setFormData] = useState({
    title: idea?.title || '',
    content: idea?.content || '',
    category: idea?.category || 'General',
    tags: idea?.tags || []
  });
  const [newTag, setNewTag] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.content.trim()) return;
    onSave(formData);
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{idea ? 'Edit Idea' : 'New Idea'}</h2>
          <button onClick={onCancel} className="modal-close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="idea-form">
          <div className="form-group">
            <label htmlFor="title">Title</label>
            <input
              id="title"
              type="text"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Enter idea title..."
              className="form-input"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="content">Content</label>
            <textarea
              id="content"
              value={formData.content}
              onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
              placeholder="Describe your idea..."
              className="form-textarea"
              rows="6"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="category">Category</label>
            <select
              id="category"
              value={formData.category}
              onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
              className="form-select"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label>Tags</label>
            <div className="tag-input-container">
              <input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                placeholder="Add a tag..."
                className="tag-input"
              />
              <button type="button" onClick={addTag} className="tag-add-btn">Add</button>
            </div>
            <div className="current-tags">
              {formData.tags.map((tag, index) => (
                <TagBadge 
                  key={index} 
                  tag={tag} 
                  removable 
                  onRemove={() => removeTag(tag)} 
                />
              ))}
            </div>
          </div>
          
          <div className="form-actions">
            <button type="button" onClick={onCancel} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              {idea ? 'Update' : 'Create'} Idea
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const App = () => {
  const [ideas, setIdeas] = useState([]);
  const [filteredIdeas, setFilteredIdeas] = useState([]);
  const [categories, setCategories] = useState(['General', 'Work', 'Personal', 'Business']);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingIdea, setEditingIdea] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');

  // Fetch data
  const fetchIdeas = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/ideas`);
      setIdeas(response.data);
      setFilteredIdeas(response.data);
    } catch (error) {
      console.error('Error fetching ideas:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      const fetchedCategories = response.data.categories;
      const allCategories = [...new Set(['General', 'Work', 'Personal', 'Business', ...fetchedCategories])];
      setCategories(allCategories);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  useEffect(() => {
    fetchIdeas();
    fetchCategories();
  }, []);

  // Filter ideas based on search and status
  useEffect(() => {
    let filtered = ideas;

    // Filter by status
    if (activeFilter !== 'all') {
      filtered = filtered.filter(idea => idea.status === activeFilter);
    }

    // Filter by search term
    if (searchTerm.trim()) {
      filtered = filtered.filter(idea =>
        idea.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        idea.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        idea.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    setFilteredIdeas(filtered);
  }, [ideas, activeFilter, searchTerm]);

  // Calculate counts for filter tabs
  const ideaCounts = {
    all: ideas.length,
    active: ideas.filter(idea => idea.status === 'active').length,
    archived: ideas.filter(idea => idea.status === 'archived').length
  };

  // CRUD operations
  const handleSaveIdea = async (formData) => {
    try {
      if (editingIdea) {
        await axios.put(`${API}/ideas/${editingIdea.id}`, formData);
      } else {
        await axios.post(`${API}/ideas`, formData);
      }
      fetchIdeas();
      fetchCategories();
      setShowForm(false);
      setEditingIdea(null);
    } catch (error) {
      console.error('Error saving idea:', error);
    }
  };

  const handleDeleteIdea = async (ideaId) => {
    if (window.confirm('Are you sure you want to delete this idea?')) {
      try {
        await axios.delete(`${API}/ideas/${ideaId}`);
        fetchIdeas();
      } catch (error) {
        console.error('Error deleting idea:', error);
      }
    }
  };

  const handleArchiveIdea = async (ideaId) => {
    try {
      await axios.patch(`${API}/ideas/${ideaId}/archive`);
      fetchIdeas();
    } catch (error) {
      console.error('Error archiving idea:', error);
    }
  };

  const handleUnarchiveIdea = async (ideaId) => {
    try {
      await axios.patch(`${API}/ideas/${ideaId}/unarchive`);
      fetchIdeas();
    } catch (error) {
      console.error('Error unarchiving idea:', error);
    }
  };

  const handleEditIdea = (idea) => {
    setEditingIdea(idea);
    setShowForm(true);
  };

  const handleNewIdea = () => {
    setEditingIdea(null);
    setShowForm(true);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading your ideas...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <Header />
      
      <main className="main-content">
        <div className="content-container">
          {/* Search and Actions */}
          <div className="content-header">
            <SearchBar 
              searchTerm={searchTerm}
              setSearchTerm={setSearchTerm}
              onSearch={() => {}}
            />
            <button onClick={handleNewIdea} className="btn btn-primary new-idea-btn">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              New Idea
            </button>
          </div>
          
          {/* Filter Tabs */}
          <FilterTabs 
            activeFilter={activeFilter}
            setActiveFilter={setActiveFilter}
            ideaCounts={ideaCounts}
          />
          
          {/* Ideas List */}
          <div className="ideas-container">
            {filteredIdeas.length === 0 ? (
              <div className="empty-state">
                <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 19c-5 0-8-3-8-9s3-9 8-9 8 3 8 9-3 9-8 9z"/>
                  <path d="M12 12l8-8"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <h3>No ideas found</h3>
                <p>
                  {searchTerm ? 'Try adjusting your search terms' : 'Start by creating your first idea!'}
                </p>
              </div>
            ) : (
              <div className="ideas-grid">
                {filteredIdeas.map(idea => (
                  <IdeaCard
                    key={idea.id}
                    idea={idea}
                    onEdit={handleEditIdea}
                    onDelete={handleDeleteIdea}
                    onArchive={handleArchiveIdea}
                    onUnarchive={handleUnarchiveIdea}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
      
      {/* Form Modal */}
      {showForm && (
        <IdeaForm
          idea={editingIdea}
          categories={categories}
          onSave={handleSaveIdea}
          onCancel={() => {
            setShowForm(false);
            setEditingIdea(null);
          }}
        />
      )}
    </div>
  );
};

export default App;
