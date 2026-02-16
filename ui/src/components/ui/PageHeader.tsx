import {
    Box,
    Container,
    Stack,
    Title,
    Text,
    Group,
    Menu,
    ActionIcon,
} from '@mantine/core';
import { useMediaQuery } from '@mantine/hooks';
import { IconDots } from '@tabler/icons-react';
import { isValidElement, createElement } from 'react';

export interface MenuItem {
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
    color?: string;
    disabled?: boolean;
    divider?: boolean;
}

interface PageHeaderProps {
    title: string | React.ReactNode;
    description?: string;
    actions?: React.ReactNode;
    badge?: React.ReactNode;
    icon?: React.ReactNode | React.ComponentType<{ size?: number }>;
    children?: React.ReactNode;
    headerBackgroundColor?: string;
    menuItems?: MenuItem[];
    headerContent?: React.ReactNode;
}

/**
 * Reusable page header component with consistent styling
 * Layout-agnostic: does not handle sidebar margins (handled by layout components)
 */
export default function PageHeader({
    title,
    description,
    actions,
    badge,
    icon,
    children,
    headerBackgroundColor,
    menuItems,
    headerContent,
}: PageHeaderProps) {
    const isMobile = useMediaQuery('(max-width: 768px)');

    // If headerBackgroundColor is provided, use it as text color (not background)
    if (headerBackgroundColor) {
        const textColor = headerBackgroundColor; // Use the color directly as text color

        // Render menu if menuItems provided
        const renderMenu = () => {
            if (!menuItems || menuItems.length === 0) return null;

            return (
                <Menu shadow="md" width={200}>
                    <Menu.Target>
                        <ActionIcon
                            variant="light"
                            size="lg"
                            aria-label="Page actions"
                            style={{
                                color: textColor,
                            }}
                        >
                            <IconDots size={18} />
                        </ActionIcon>
                    </Menu.Target>
                    <Menu.Dropdown>
                        {menuItems.map((item, index) => {
                            if (item.divider) {
                                return (
                                    <Menu.Divider key={`divider-${index}`} />
                                );
                            }
                            return (
                                <Menu.Item
                                    key={index}
                                    leftSection={item.icon}
                                    onClick={item.onClick}
                                    color={item.color}
                                    disabled={item.disabled}
                                >
                                    {item.label}
                                </Menu.Item>
                            );
                        })}
                    </Menu.Dropdown>
                </Menu>
            );
        };

        return (
            <>
                {/* Header bar with colored text - aligned with container padding */}
                {/* On mobile, add top margin to account for navbar (breadcrumbs are hidden) */}
                <Container
                    size="md"
                    mt={isMobile ? '70px' : 'xl'}
                    px={{ base: 'sm', sm: 'md' }}
                >
                    <Box
                        style={{
                            textTransform: 'uppercase',
                            padding: '16px 0 4px 0',
                            borderRadius: 0,
                            borderBottom: `3px solid ${textColor}`,
                        }}
                    >
                        {headerContent ? (
                            <Group
                                justify="space-between"
                                align="center"
                                wrap={isMobile ? 'wrap' : 'nowrap'}
                            >
                                {headerContent}
                                <Group gap="xs" align="center">
                                    {renderMenu()}
                                    {actions}
                                </Group>
                            </Group>
                        ) : isMobile ? (
                            <Stack gap="sm">
                                <Group justify="space-between" align="center">
                                    <Group gap="sm" align="center" wrap="wrap">
                                        {icon && (
                                            <div
                                                className="flex items-center"
                                                style={{
                                                    color: textColor,
                                                }}
                                            >
                                                {isValidElement(icon)
                                                    ? icon
                                                    : createElement(
                                                          icon as React.ComponentType<{
                                                              size?: number;
                                                          }>,
                                                          {
                                                              size: 24,
                                                          }
                                                      )}
                                            </div>
                                        )}
                                        <Title
                                            order={1}
                                            style={{
                                                color: textColor,
                                                margin: 0,
                                                fontSize: '1.5rem',
                                            }}
                                        >
                                            {title}
                                        </Title>
                                    </Group>
                                    <Group gap="xs" align="center">
                                        {renderMenu()}
                                        {actions}
                                    </Group>
                                </Group>
                                {badge && <Box>{badge}</Box>}
                            </Stack>
                        ) : (
                            <Group justify="space-between" align="center">
                                <Group gap="md" align="center">
                                    {icon && (
                                        <div
                                            style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                color: textColor,
                                            }}
                                        >
                                            {isValidElement(icon)
                                                ? icon
                                                : createElement(
                                                      icon as React.ComponentType<{
                                                          size?: number;
                                                      }>,
                                                      {
                                                          size: 28,
                                                      }
                                                  )}
                                        </div>
                                    )}
                                    <Title
                                        order={1}
                                        style={{
                                            color: textColor,
                                            margin: 0,
                                        }}
                                    >
                                        {title}
                                    </Title>
                                    {badge}
                                </Group>
                                <Group gap="xs" align="center">
                                    {renderMenu()}
                                    {actions}
                                </Group>
                            </Group>
                        )}
                    </Box>
                </Container>

                {/* Description and children in container */}
                <Container size="md" px={{ base: 'sm', sm: 'md' }}>
                    <Stack gap="sm">
                        {description && (
                            <Text mt="sm" size={isMobile ? 'sm' : 'md'}>
                                {description}
                            </Text>
                        )}
                        {children && (
                            <div style={{ marginTop: '1rem' }}>{children}</div>
                        )}
                    </Stack>
                </Container>
            </>
        );
    }

    // Standard header layout (no background color)
    // On mobile, add top margin to account for navbar (breadcrumbs are hidden)
    // On desktop, use paddingTop as breadcrumbs provide the top spacing
    const boxStyles: React.CSSProperties = {
        paddingTop: isMobile ? 0 : '40px',
        marginTop: isMobile ? '70px' : 0,
    };

    // Render menu if menuItems provided (for standard layout)
    const renderMenu = () => {
        if (!menuItems || menuItems.length === 0) return null;

        return (
            <Menu shadow="md" width={200}>
                <Menu.Target>
                    <ActionIcon
                        variant="light"
                        size="lg"
                        aria-label="Page actions"
                    >
                        <IconDots size={18} />
                    </ActionIcon>
                </Menu.Target>
                <Menu.Dropdown>
                    {menuItems.map((item, index) => {
                        if (item.divider) {
                            return <Menu.Divider key={`divider-${index}`} />;
                        }
                        return (
                            <Menu.Item
                                key={index}
                                leftSection={item.icon}
                                onClick={item.onClick}
                                color={item.color}
                                disabled={item.disabled}
                            >
                                {item.label}
                            </Menu.Item>
                        );
                    })}
                </Menu.Dropdown>
            </Menu>
        );
    };

    return (
        <Box style={boxStyles}>
            <Container size="md" px={{ base: 'sm', sm: 'md' }}>
                <Stack gap="sm">
                    {isMobile ? (
                        <Stack gap="sm">
                            <Group
                                gap="sm"
                                align="center"
                                justify="space-between"
                                wrap="wrap"
                            >
                                <Group gap="sm" align="center" wrap="wrap">
                                    {icon && (
                                        <div className="flex items-center">
                                            {isValidElement(icon)
                                                ? icon
                                                : createElement(
                                                      icon as React.ComponentType<{
                                                          size?: number;
                                                      }>,
                                                      {
                                                          size: 24,
                                                      }
                                                  )}
                                        </div>
                                    )}
                                    <Title
                                        order={1}
                                        style={{ fontSize: '1.5rem' }}
                                    >
                                        {title}
                                    </Title>
                                </Group>
                                <Group gap="xs" align="center">
                                    {renderMenu()}
                                    {actions}
                                </Group>
                            </Group>
                            {badge && <Box>{badge}</Box>}
                            {description && (
                                <Text mt="sm" size="sm">
                                    {description}
                                </Text>
                            )}
                            {children && (
                                <div style={{ marginTop: '1rem' }}>
                                    {children}
                                </div>
                            )}
                        </Stack>
                    ) : (
                        <Group
                            gap="md"
                            align="flex-start"
                            justify="space-between"
                            wrap="wrap"
                        >
                            <Group
                                gap="md"
                                align="flex-start"
                                style={{ flex: 1 }}
                            >
                                <div style={{ flex: 1 }}>
                                    <Group
                                        gap="md"
                                        align="center"
                                        mb="xs"
                                        wrap="wrap"
                                    >
                                        {icon && (
                                            <div
                                                style={{
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                }}
                                            >
                                                {isValidElement(icon)
                                                    ? icon
                                                    : createElement(
                                                          icon as React.ComponentType<{
                                                              size?: number;
                                                          }>,
                                                          {
                                                              size: 28,
                                                          }
                                                      )}
                                            </div>
                                        )}
                                        <Title order={1}>{title}</Title>
                                        {badge}
                                    </Group>
                                    {description && (
                                        <Text mt="sm" size="md">
                                            {description}
                                        </Text>
                                    )}
                                    {children && (
                                        <div style={{ marginTop: '1rem' }}>
                                            {children}
                                        </div>
                                    )}
                                </div>
                            </Group>
                            <Group gap="xs" align="flex-start">
                                {renderMenu()}
                                {actions}
                            </Group>
                        </Group>
                    )}
                </Stack>
            </Container>
        </Box>
    );
}
