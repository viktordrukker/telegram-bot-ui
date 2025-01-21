import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../Layout';

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('Layout Component', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  test('renders header and navigation', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    );

    expect(screen.getByText('Telegram Bot Management')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Bot Management')).toBeInTheDocument();
    expect(screen.getByText('Advertising')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
  });

  test('navigates when menu items are clicked', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test Content</div>
        </Layout>
      </BrowserRouter>
    );

    fireEvent.click(screen.getByText('Dashboard'));
    expect(mockNavigate).toHaveBeenCalledWith('/');

    fireEvent.click(screen.getByText('Bot Management'));
    expect(mockNavigate).toHaveBeenCalledWith('/bots');

    fireEvent.click(screen.getByText('Advertising'));
    expect(mockNavigate).toHaveBeenCalledWith('/advertising');

    fireEvent.click(screen.getByText('Analytics'));
    expect(mockNavigate).toHaveBeenCalledWith('/analytics');
  });

  test('renders children content', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Test Child Content</div>
        </Layout>
      </BrowserRouter>
    );

    expect(screen.getByText('Test Child Content')).toBeInTheDocument();
  });
});